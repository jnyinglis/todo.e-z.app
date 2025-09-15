import { useEffect } from 'react';

interface SEOHeadProps {
  title?: string;
  description?: string;
  keywords?: string;
  canonical?: string;
  robots?: string;
  ogTitle?: string;
  ogDescription?: string;
  ogImage?: string;
  ogType?: string;
  twitterCard?: string;
  twitterSite?: string;
  twitterCreator?: string;
  jsonLD?: object;
}

const DEFAULT_SEO = {
  title: 'Vite React FastAPI Template',
  description: 'A modern full-stack template with React, FastAPI, and PostgreSQL featuring secure authentication and responsive design.',
  keywords: 'react, fastapi, postgresql, template, authentication, full-stack, typescript, python',
  ogType: 'website',
  twitterCard: 'summary_large_image'
};

export function SEOHead({
  title,
  description = DEFAULT_SEO.description,
  keywords = DEFAULT_SEO.keywords,
  canonical,
  robots,
  ogTitle,
  ogDescription,
  ogImage,
  ogType = DEFAULT_SEO.ogType,
  twitterCard = DEFAULT_SEO.twitterCard,
  twitterSite,
  twitterCreator,
  jsonLD
}: SEOHeadProps) {
  const fullTitle = title ? `${title} | ${DEFAULT_SEO.title}` : DEFAULT_SEO.title;
  const finalOgTitle = ogTitle || fullTitle;
  const finalOgDescription = ogDescription || description;

  useEffect(() => {
    // Update document title
    document.title = fullTitle;

    // Helper function to set or update meta tags
    const setMetaTag = (name: string, content: string, attribute: string = 'name') => {
      let element = document.querySelector(`meta[${attribute}="${name}"]`);
      if (!element) {
        element = document.createElement('meta');
        element.setAttribute(attribute, name);
        document.head.appendChild(element);
      }
      element.setAttribute('content', content);
    };

    // Helper function to set or update link tags
    const setLinkTag = (rel: string, href: string) => {
      let element = document.querySelector(`link[rel="${rel}"]`);
      if (!element) {
        element = document.createElement('link');
        element.setAttribute('rel', rel);
        document.head.appendChild(element);
      }
      element.setAttribute('href', href);
    };

    // Basic meta tags
    setMetaTag('description', description);
    setMetaTag('keywords', keywords);
    setMetaTag('viewport', 'width=device-width, initial-scale=1.0');
    setMetaTag('robots', robots || 'index, follow');
    setMetaTag('author', 'Your Company Name');

    // Open Graph meta tags
    setMetaTag('og:title', finalOgTitle, 'property');
    setMetaTag('og:description', finalOgDescription, 'property');
    setMetaTag('og:type', ogType, 'property');
    setMetaTag('og:site_name', DEFAULT_SEO.title, 'property');

    if (ogImage) {
      setMetaTag('og:image', ogImage, 'property');
      setMetaTag('og:image:alt', finalOgTitle, 'property');
    }

    if (canonical) {
      setMetaTag('og:url', canonical, 'property');
      setLinkTag('canonical', canonical);
    }

    // Twitter Card meta tags
    setMetaTag('twitter:card', twitterCard);
    setMetaTag('twitter:title', finalOgTitle);
    setMetaTag('twitter:description', finalOgDescription);

    if (twitterSite) {
      setMetaTag('twitter:site', twitterSite);
    }

    if (twitterCreator) {
      setMetaTag('twitter:creator', twitterCreator);
    }

    if (ogImage) {
      setMetaTag('twitter:image', ogImage);
    }

    // Additional SEO meta tags
    setMetaTag('theme-color', '#646cff');
    setMetaTag('msapplication-TileColor', '#646cff');

    // JSON-LD structured data
    if (jsonLD) {
      let scriptElement = document.querySelector('script[type="application/ld+json"]');
      if (!scriptElement) {
        scriptElement = document.createElement('script');
        scriptElement.setAttribute('type', 'application/ld+json');
        document.head.appendChild(scriptElement);
      }
      scriptElement.textContent = JSON.stringify(jsonLD);
    }

  }, [
    fullTitle, description, keywords, canonical, robots, finalOgTitle,
    finalOgDescription, ogImage, ogType, twitterCard, twitterSite,
    twitterCreator, jsonLD
  ]);

  return null; // This component only manages head elements
}

