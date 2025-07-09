import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Extracts main keywords from a query string (simple stopword removal)
export function extractKeywords(query: string): string[] {
  const stopwords = new Set([
    'the', 'is', 'in', 'at', 'of', 'on', 'and', 'a', 'to', 'for', 'with', 'by', 'an', 'be', 'can', 'as', 'are', 'from', 'that', 'this', 'it', 'or', 'what', 'how', 'do', 'does', 'which', 'these', 'those', 'such', 'so', 'but', 'if', 'then', 'than', 'into', 'about', 'per', 'their', 'will', 'has', 'have', 'had', 'was', 'were', 'not', 'also', 'may', 'should', 'could', 'would', 'when', 'where', 'why', 'who', 'whom', 'whose', 'been', 'being', 'because', 'while', 'during', 'after', 'before', 'above', 'below', 'between', 'among', 'over', 'under', 'again', 'further', 'once', 'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'don', 'now'
  ]);
  return query
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .split(/\s+/)
    .filter(word => word && !stopwords.has(word));
}
