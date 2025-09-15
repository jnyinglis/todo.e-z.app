# SEO Implementation Guide

This template includes comprehensive SEO features to improve search engine visibility and social media sharing.

## Features Implemented

### 🤖 Robots.txt & Sitemaps
- **Static robots.txt**: `/frontend/public/robots.txt`
- **Dynamic sitemap**: Backend endpoint `/sitemap.xml`
- **Environment-aware**: Different rules for production vs development

### 📋 Meta Tags & Open Graph
- **SEOHead Component**: Dynamic meta tag management
- **Open Graph**: Complete Facebook/LinkedIn sharing support
- **Twitter Cards**: Optimized for Twitter sharing
- **Mobile optimized**: PWA-ready meta tags

### 🔍 Structured Data (JSON-LD)
- **Schema.org support**: Website, Organization, and WebPage schemas
- **Search engine optimization**: Rich snippets support
- **Flexible implementation**: Easy to extend for blog posts, products, etc.

### 🛡️ Security & Standards
- **security.txt**: Responsible disclosure information
- **PWA manifest**: Progressive Web App support
- **Performance**: Preconnect hints for external resources

## Usage Examples

### Basic SEO Implementation
```tsx
import { SEOHead, createWebsiteSchema } from './components/SEOHead';

function HomePage() {
  const websiteSchema = createWebsiteSchema(
    'Your Site Name',
    'https://yoursite.com',
    'Your site description'
  );

  return (
    <>
      <SEOHead
        title="Home"
        description="Welcome to our amazing site"
        canonical="https://yoursite.com"
        jsonLD={websiteSchema}
      />
      {/* Your component content */}
    </>
  );
}
```

### Dynamic Content SEO
```tsx
// For blog posts, products, etc.
<SEOHead
  title={post.title}
  description={post.excerpt}
  canonical={`https://yoursite.com/posts/${post.slug}`}
  ogImage={post.featuredImage}
  ogType="article"
  jsonLD={{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": post.title,
    "datePublished": post.publishedAt,
    "author": {
      "@type": "Person",
      "name": post.author.name
    }
  }}
/>
```

### Private/Admin Pages
```tsx
// Prevent indexing of admin areas
<SEOHead
  title="Admin Dashboard"
  robots="noindex, nofollow"
/>
```

## Backend Endpoints

### Sitemap Generation
- **URL**: `/sitemap.xml`
- **Features**: Dynamic URL generation, caching, environment awareness
- **Customization**: Add your dynamic content URLs in `backend/app/api/seo.py`

### Security & SEO Files
- **robots.txt**: `/robots.txt` (served by backend)
- **security.txt**: `/.well-known/security.txt`

## Customization Guide

### 1. Update Default SEO Values
Edit `frontend/src/components/SEOHead.tsx`:
```tsx
const DEFAULT_SEO = {
  title: 'Your Site Name',
  description: 'Your site description',
  keywords: 'your, keywords, here',
  ogType: 'website',
  twitterCard: 'summary_large_image'
};
```

### 2. Add Dynamic URLs to Sitemap
Edit `backend/app/api/seo.py`:
```python
# Add database queries to generate dynamic URLs
async with get_session() as session:
    posts = await session.execute(select(Post).where(Post.published == True))
    for post in posts:
        base_urls.append({
            "loc": f"{settings.frontend_url}/posts/{post.slug}",
            "lastmod": post.updated_at.isoformat(),
            "changefreq": "weekly",
            "priority": "0.6"
        })
```

### 3. Configure robots.txt
Update domain in `frontend/public/robots.txt` and `backend/app/api/seo.py`

### 4. Update security.txt
Edit contact information in:
- `frontend/public/.well-known/security.txt`
- `backend/app/api/seo.py` (security endpoint)

## Best Practices

### 1. Title Tags
- Keep under 60 characters
- Include primary keyword
- Use format: "Page Title | Site Name"

### 2. Meta Descriptions
- Keep 150-160 characters
- Include call-to-action
- Unique for each page

### 3. Open Graph Images
- Size: 1200x630px minimum
- Format: PNG or JPG
- Include text overlay for better engagement

### 4. Structured Data
- Use Schema.org vocabulary
- Test with Google's Rich Results Test
- Include breadcrumbs for navigation

### 5. URL Structure
- Use hyphens for word separation
- Keep URLs short and descriptive
- Include primary keywords

## Testing & Validation

### Tools for Testing
1. **Google Search Console**: Monitor search performance
2. **Facebook Debugger**: Test Open Graph tags
3. **Twitter Card Validator**: Verify Twitter sharing
4. **Schema.org Validator**: Test structured data
5. **PageSpeed Insights**: Check performance impact

### Checklist
- [ ] All pages have unique titles and descriptions
- [ ] Open Graph tags work correctly
- [ ] Structured data validates without errors
- [ ] robots.txt allows important pages
- [ ] Sitemap includes all important URLs
- [ ] Mobile-friendly design
- [ ] Fast loading times

## Production Deployment

### Environment Variables
Set these in production:
```bash
FRONTEND_URL=https://yourdomain.com
ENVIRONMENT=production
```

### CDN Configuration
- Serve static assets from CDN
- Set proper cache headers for SEO files:
  - robots.txt: 24 hours
  - sitemap.xml: 1 hour
  - security.txt: 24 hours

### Analytics Integration
Consider adding:
- Google Analytics 4
- Google Search Console
- Social media pixels (if needed)

## Additional Recommendations

### Content Strategy
1. **Blog/Content Section**: Add a blog for fresh content
2. **FAQ Pages**: Great for long-tail keywords
3. **About/Team Pages**: Build authority and trust
4. **Contact Information**: Clear contact details

### Technical SEO
1. **HTTPS**: Ensure SSL certificate is properly configured
2. **Site Speed**: Optimize images and bundle sizes
3. **Core Web Vitals**: Monitor and improve performance metrics
4. **Mobile-First**: Ensure responsive design works perfectly

### Local SEO (if applicable)
1. **Google My Business**: Create and optimize listing
2. **Local Schema**: Add LocalBusiness structured data
3. **NAP Consistency**: Name, Address, Phone consistent everywhere

This SEO implementation provides a solid foundation for search engine optimization while remaining flexible and easy to customize for your specific needs.