import { test, describe, it, expect, vi, afterEach } from 'vitest';
import { mappingDocsToArticles,  type Article } from './article-utils';
import { render, screen, waitFor, cleanup } from '@testing-library/svelte'
import App from './App.svelte'
//reference: https://vitest.dev/api/

describe('mappingDocsToArticles', () => {
    it('should return an Article with image when multimedia.default.url is present', () => {
      const docs = [
        {
          headline: { main: 'Tester Article with image' },
          snippet: 'This article has a default image.',
          web_url: 'https://tester1.com/with-image',
          multimedia: {
            default: {
              url: 'https://tester1.com/image.jpg'
            }
          }
        }
      ];
  
      const result: Article[] = mappingDocsToArticles(docs);
  
      expect(result[0].title).toBe('Tester Article with image');
      expect(result[0].picture).toBe('https://tester1.com/image.jpg');
      expect(result[0].url).toBe('https://tester1.com/with-image');
    });
  
    it('should return an Article with undefined picture when multimedia.default is missing', () => {
      const docs = [
        {
          headline: { main: 'Tester2 Article without image' },
          snippet: 'No image for this article.',
          web_url: 'https://tester2example.com/no-image',
          multimedia: {}
        }
      ];
  
      const result: Article[] = mappingDocsToArticles(docs);
  
      expect(result[0].title).toBe('Tester2 Article without image');
      expect(result[0].picture).toBe(undefined); //simulating no image
      expect(result[0].url).toBe('https://tester2example.com/no-image');
    });
  });
//referenced: https://stackoverflow.com/questions/76754014/reactjs-how-to-unit-test-login-form-in-vitest
  describe('User login check', () => {
    afterEach(() => {
      vi.restoreAllMocks();
      cleanup(); // 
    });
  
    it('shows Login button if user is NOT logged in', async () => {
      vi.stubGlobal('fetch', vi.fn((url) => {
        if (url.includes('/auth/user')) {
          return Promise.resolve({
            status: 401,//error
            json: () => Promise.resolve({ error: 'Not authenticated' }),
          });
        }
        return Promise.resolve({
          status: 200,//yes it worked
          json: () => Promise.resolve({ apiKey: 'TesterKey', response: { docs: [] } }),
        });
      }));
  
      render(App);
  
      await waitFor(() => {
        expect(screen.getByText('Login')).toBeInTheDocument();
      });
    });
  
    it('shows account icon if user IS logged in', async () => {
      vi.stubGlobal('fetch', vi.fn((url) => {
        if (url.includes('/auth/user')) {
          return Promise.resolve({
            status: 200,
            json: () => Promise.resolve({ email: 'user@tester.com', username: 'user' }),
          });
        }
        return Promise.resolve({
          status: 200,
          json: () => Promise.resolve({ apiKey: 'TesterKey', response: { docs: [] } }),
        });
      }));
  
      render(App);
  
      await waitFor(() => {
        expect(screen.getByLabelText('User Account')).toBeInTheDocument();
      });
    });
  });

