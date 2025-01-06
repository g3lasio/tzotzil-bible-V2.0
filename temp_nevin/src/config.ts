
export const API_URL = 'https://sistema-nevin.replit.app';
export const API_VERSION = 'v1';
export const ENDPOINTS = {
  auth: {
    login: '/api/auth/login',
    register: '/api/auth/register',
    verify: '/api/auth/verify',
  },
  bible: {
    books: '/api/bible/books',
    chapters: '/api/bible/chapters',
    verses: '/api/bible/verses',
  },
  nevin: {
    chat: '/api/nevin/chat',
    query: '/api/nevin/query'
  }
};
