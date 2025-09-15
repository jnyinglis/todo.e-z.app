// Structured data schemas for SEO
const DEFAULT_SEO = {
  title: 'Vite React FastAPI Template',
  description: 'A modern full-stack template with React, FastAPI, and PostgreSQL featuring secure authentication and responsive design.',
  image: '/icon-512.svg',
  url: 'https://your-domain.com'
};

// Predefined structured data schemas
export const createWebsiteSchema = (name: string, url: string, description: string) => ({
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": name,
  "url": url,
  "description": description,
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": `${url}/search?q={search_term_string}`
    },
    "query-input": "required name=search_term_string"
  }
});

export const createOrganizationSchema = (name: string, url: string, logo?: string) => ({
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": name,
  "url": url,
  ...(logo && { "logo": logo })
});

export const createWebPageSchema = (name: string, url: string, description: string) => ({
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": name,
  "url": url,
  "description": description,
  "isPartOf": {
    "@type": "WebSite",
    "name": DEFAULT_SEO.title
  }
});