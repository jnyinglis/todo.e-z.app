from typing import List
from fastapi import APIRouter, Response
from datetime import datetime
from app.core.config import settings
from app.schemas.response import TextResponse

router = APIRouter()


@router.get("/sitemap.xml", response_class=Response, responses={200: {"content": {"application/xml": {}}}})
async def get_sitemap() -> Response:
    """Generate dynamic XML sitemap"""

    # Base URLs for the application
    base_urls = [
        {
            "loc": f"{settings.frontend_url}/",
            "lastmod": datetime.now().isoformat(),
            "changefreq": "daily",
            "priority": "1.0"
        },
        {
            "loc": f"{settings.frontend_url}/auth/login",
            "lastmod": datetime.now().isoformat(),
            "changefreq": "monthly",
            "priority": "0.8"
        },
        {
            "loc": f"{settings.frontend_url}/auth/register",
            "lastmod": datetime.now().isoformat(),
            "changefreq": "monthly",
            "priority": "0.8"
        }
    ]

    # TODO: Add dynamic URLs from database (blog posts, user profiles, etc.)
    # Example:
    # async with get_session() as session:
    #     # Get dynamic content URLs
    #     posts = await session.execute(select(Post).where(Post.published == True))
    #     for post in posts:
    #         base_urls.append({
    #             "loc": f"{settings.frontend_url}/posts/{post.slug}",
    #             "lastmod": post.updated_at.isoformat(),
    #             "changefreq": "weekly",
    #             "priority": "0.6"
    #         })

    # Generate XML sitemap
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in base_urls:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{url["loc"]}</loc>\n'
        xml_content += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
        xml_content += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        xml_content += f'    <priority>{url["priority"]}</priority>\n'
        xml_content += '  </url>\n'

    xml_content += '</urlset>'

    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={"Cache-Control": "max-age=3600"}  # Cache for 1 hour
    )


@router.get("/robots.txt", response_class=Response, responses={200: {"content": {"text/plain": {}}}})
async def get_robots() -> Response:
    """Serve robots.txt with environment-specific rules"""

    if settings.environment == "production":
        robots_content = """User-agent: *
Allow: /

# Sitemap location
Sitemap: {base_url}/sitemap.xml

# Disallow admin and auth areas
Disallow: /auth/
Disallow: /admin/
Disallow: /api/

# Allow common crawlers
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /""".format(base_url=settings.frontend_url)
    else:
        # Block all crawlers in development/staging
        robots_content = """User-agent: *
Disallow: /"""

    return Response(
        content=robots_content,
        media_type="text/plain",
        headers={"Cache-Control": "max-age=86400"}  # Cache for 24 hours
    )


@router.get("/.well-known/security.txt", response_class=Response, responses={200: {"content": {"text/plain": {}}}})
async def get_security_txt() -> Response:
    """Security.txt for responsible disclosure"""

    security_content = """Contact: security@yourdomain.com
Expires: 2025-12-31T23:59:59.000Z
Acknowledgments: https://yourdomain.com/security/acknowledgments
Policy: https://yourdomain.com/security/policy
Preferred-Languages: en

# Please report security vulnerabilities responsibly"""

    return Response(
        content=security_content,
        media_type="text/plain",
        headers={"Cache-Control": "max-age=86400"}
    )