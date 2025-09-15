#!/usr/bin/env python3
"""
Generate TypeScript types from FastAPI OpenAPI schema.

This script exports the OpenAPI schema from the FastAPI application and generates
corresponding TypeScript interfaces and types for the frontend to use.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass

# Add the app directory to Python path
import sys
sys.path.append(str(Path(__file__).parent))

from main import app


@dataclass
class TypeGenConfig:
    """Configuration for type generation."""
    output_file: str = "../frontend/src/types/api.ts"
    include_examples: bool = True
    generate_client: bool = True
    namespace: str = "API"


def sanitize_name(name: str) -> str:
    """Sanitize property names for TypeScript."""
    # Remove special characters and convert to camelCase
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Convert snake_case to camelCase
    components = name.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def get_ts_type(schema: Dict[str, Any], definitions: Dict[str, Any], required_fields: Optional[Set[str]] = None, field_name: str = "") -> str:
    """Convert OpenAPI schema to TypeScript type."""
    if required_fields is None:
        required_fields = set()

    schema_type = schema.get('type')
    schema_format = schema.get('format')

    # Handle references
    if '$ref' in schema:
        ref_path = schema['$ref']
        if ref_path.startswith('#/'):
            ref_name = ref_path.split('/')[-1]
            return str(ref_name)

    # Handle arrays
    if schema_type == 'array':
        items = schema.get('items', {})
        item_type = get_ts_type(items, definitions, required_fields)
        return f"{item_type}[]"

    # Handle objects
    if schema_type == 'object' or 'properties' in schema:
        if 'properties' in schema:
            properties = []
            required = set(schema.get('required', []))

            for prop_name, prop_schema in sorted(schema['properties'].items()):
                prop_type = get_ts_type(prop_schema, definitions, required)
                optional = "?" if prop_name not in required else ""
                sanitized_name = sanitize_name(prop_name)
                properties.append(f"  {sanitized_name}{optional}: {prop_type};")

            return "{\n" + "\n".join(properties) + "\n}"
        else:
            return "Record<string, unknown>"

    # Handle unions/oneOf
    if 'oneOf' in schema or 'anyOf' in schema:
        options = schema.get('oneOf') or schema.get('anyOf') or []
        types = [get_ts_type(option, definitions, required_fields) for option in options]
        return " | ".join(types)

    # Handle enums
    if 'enum' in schema:
        enum_values = schema['enum']
        if all(isinstance(v, str) for v in enum_values):
            return " | ".join(f'"{v}"' for v in enum_values)
        else:
            return " | ".join(str(v) for v in enum_values)

    # Handle primitive types
    type_mapping = {
        'string': 'string',
        'integer': 'number',
        'number': 'number',
        'boolean': 'boolean',
        'null': 'null',
    }

    # Handle string formats
    if schema_type == 'string':
        if schema_format in ['date-time', 'date', 'time']:
            return 'string' # Keep as string for JSON serialization
        elif schema_format == 'email':
            return 'string'
        elif schema_format == 'uuid':
            return 'string'

    return type_mapping.get(schema_type or 'unknown', 'unknown')


def generate_interface(name: str, schema: Dict[str, Any], definitions: Dict[str, Any]) -> str:
    """Generate a TypeScript interface from a schema."""
    properties = []
    required = set(schema.get('required', []))

    if 'properties' in schema:
        for prop_name, prop_schema in sorted(schema['properties'].items()):
            prop_type = get_ts_type(prop_schema, definitions, required)
            optional = "?" if prop_name not in required else ""
            sanitized_name = sanitize_name(prop_name)

            # Add JSDoc comment if description exists
            description = prop_schema.get('description', '')
            if description:
                properties.append(f"  /** {description} */")

            properties.append(f"  {sanitized_name}{optional}: {prop_type};")

    description = schema.get('description', '')
    interface_comment = f"/** {description} */" if description else ""

    interface_body = "\n".join(properties) if properties else "  [key: string]: any;"

    return f"""
{interface_comment}
export interface {name} {{
{interface_body}
}}"""


def generate_api_client(paths: Dict[str, Any], definitions: Dict[str, Any]) -> str:
    """Generate a simple API client with typed methods."""
    client_methods = []

    for path, methods in sorted(paths.items()):
        for method, operation in sorted(methods.items()):
            if method.lower() not in ['get', 'post', 'put', 'patch', 'delete']:
                continue

            operation_id = operation.get('operationId', '')
            if not operation_id:
                continue

            # Generate method name
            method_name = sanitize_name(operation_id)

            # Get request/response types
            request_body = operation.get('requestBody', {})
            responses = operation.get('responses', {})

            # Parameters
            parameters = operation.get('parameters', [])
            path_params = [p for p in parameters if p.get('in') == 'path']
            query_params = [p for p in parameters if p.get('in') == 'query']

            # Build parameter types
            param_types = []
            if path_params:
                for param in path_params:
                    param_name = sanitize_name(param['name'])
                    param_schema = param.get('schema', {})
                    param_type = get_ts_type(param_schema, definitions)
                    param_types.append(f"{param_name}: {param_type}")

            # Request body type
            request_type = None
            if request_body and 'content' in request_body:
                content = request_body['content']
                if 'application/json' in content:
                    request_schema = content['application/json'].get('schema', {})
                    request_type = get_ts_type(request_schema, definitions)

            # Response type
            response_type = 'unknown'
            if '200' in responses:
                response_content = responses['200'].get('content', {})
                if 'application/json' in response_content:
                    response_schema = response_content['application/json'].get('schema', {})
                    response_type = get_ts_type(response_schema, definitions)
                elif 'text/plain' in response_content:
                    response_type = 'string'
                elif 'application/xml' in response_content:
                    response_type = 'string'

            # Build method signature
            if request_type:
                param_types.append(f"data: {request_type}")

            params_str = ", ".join(param_types)

            # Generate method
            http_method = method.upper()
            # Determine response parsing based on content type
            response_parsing = "response.json()"
            if response_type == 'string':
                # Check if this is a text/xml endpoint
                if '200' in responses:
                    response_content = responses['200'].get('content', {})
                    if 'text/plain' in response_content or 'application/xml' in response_content:
                        response_parsing = "response.text()"

            client_methods.append(f"""
  async {method_name}({params_str}): Promise<{response_type}> {{
    const response = await this.fetch('{path}', {{
      method: '{http_method}',{f'''
      body: JSON.stringify(data),''' if request_type else ''}
    }});
    return {response_parsing};
  }}""")

    return f"""
export class ApiClient {{
  private baseUrl: string;
  private fetchFn: typeof fetch;

  constructor(baseUrl: string = '/api', fetchFn: typeof fetch = fetch) {{
    this.baseUrl = baseUrl;
    this.fetchFn = fetchFn;
  }}

  private async fetch(path: string, options: RequestInit = {{}}) {{
    const url = `${{this.baseUrl}}${{path}}`;
    const defaultHeaders: HeadersInit = {{
      'Content-Type': 'application/json',
    }};

    const token = localStorage.getItem('access_token');
    if (token) {{
      (defaultHeaders as Record<string, string>)['Authorization'] = `Bearer ${{token}}`;
    }}

    const response = await this.fetchFn(url, {{
      ...options,
      headers: {{
        ...defaultHeaders,
        ...options.headers,
      }},
    }});

    if (!response.ok) {{
      throw new Error(`API Error: ${{response.status}} ${{response.statusText}}`);
    }}

    return response;
  }}
{"".join(client_methods)}
}}

// Default API client instance
export const apiClient = new ApiClient();"""


def main() -> None:
    """Generate TypeScript types from FastAPI OpenAPI schema."""
    config = TypeGenConfig()

    print("🔧 Generating TypeScript types from FastAPI OpenAPI schema...")

    # Get OpenAPI schema
    openapi_schema = app.openapi()

    # Extract components
    components = openapi_schema.get('components', {})
    schemas = components.get('schemas', {})
    paths = openapi_schema.get('paths', {})

    # Generate TypeScript interfaces
    interfaces = []

    # Generate interfaces for all schemas (sorted for deterministic output)
    for name, schema in sorted(schemas.items()):
        if schema.get('type') == 'object' or 'properties' in schema:
            interface = generate_interface(name, schema, schemas)
            interfaces.append(interface)

    # Generate API client if requested
    api_client = ""
    if config.generate_client:
        api_client = generate_api_client(paths, schemas)

    # Generate the complete TypeScript file
    output_content = f'''/**
 * Generated TypeScript types from FastAPI OpenAPI schema
 *
 * 🚨 DO NOT EDIT MANUALLY 🚨
 * This file is auto-generated. Run 'make generate-types' to regenerate.
 */

// API Response wrapper types
export interface ApiResponse<T> {{
  data: T;
  message?: string;
}}

export interface ApiError {{
  detail: string;
  type?: string;
}}

export interface PaginatedResponse<T> {{
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}}

// Authentication types
export interface TokenResponse {{
  access_token: string;
  token_type: string;
  expires_in?: number;
}}

{"".join(interfaces)}

{api_client}

// Utility types
export type AuthProvider = "google" | "apple" | "email";

// API endpoint types for better type safety
export interface ApiAuthGoogleRequest {{
  credential: string;
  clientId: string;
}}

export interface ApiAuthMagicLinkRequest {{
  email: string;
}}

export interface ApiAuthMagicLinkVerify {{
  token: string;
}}

export interface ApiUsersCreateRequest {{
  email: string;
  fullName?: string;
  password?: string;
}}

export interface ApiUsersUpdateRequest {{
  fullName?: string;
  avatarUrl?: string;
}}
'''

    # Ensure output directory exists
    output_path = Path(config.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the TypeScript file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print(f"✅ TypeScript types generated successfully!")
    print(f"📁 Output: {output_path.resolve()}")
    print(f"📊 Generated {len(interfaces)} interfaces")

    # Also save the raw OpenAPI schema for reference
    schema_path = output_path.parent / "openapi-schema.json"
    with open(schema_path, 'w', encoding='utf-8') as f:
        json.dump(openapi_schema, f, indent=2, sort_keys=True)

    print(f"📋 OpenAPI schema saved: {schema_path.resolve()}")


if __name__ == "__main__":
    main()