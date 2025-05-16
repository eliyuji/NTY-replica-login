## How to Run Unit Testing Files: `test_app.py`, `myTest.cy.ts`,`article-utils.test.ts`, and `article-utils.ts` (isolation testing)
To simply run the webpage, navigate to root of project file and run:
```
npm install
docker compose -f docker-compose.dev.yml up --build
```
or
```
docker compose -f docker-compose.prod.yml up --build
```
To run Unit Tests:
Navigate to the root dir of the project and run the following commands:
### Backend: (Folder: backend)
```
pip install pytest
cd backend
pytest
```
The first test is to check when NYT_API_KEY is set, the API should return the correct key. 
The second test is to check when NYT_API_KEY is not set, the API will not fail and it is still safe to return "apiKey" and that one  will be None or an empty string.

Citation: 
[pytest](https://docs.pytest.org/en/6.2.x/reference.html#pytest-fixture)


### Frontend (Testing if article data is being fetched correctly and turned into Article objects)
```
cd frontend
npm install
npm install -D vitest
npx vitest run
```
The first 2 tests check if the raw data fetched from the API can be correctly transformed into Article objects with their attributes: title, URL, image. Covers for cases where the article does/does not have an image associated.
The third test checks whether the URL string used by fetch contains Davis and Sacramento. Verify that the correct query keywords are included in the API call. The last two tests simulates an unauthenticated user (/auth/user returns 401) and checks that a "Login" button appears.
and for authenticated user (/auth/user returns user data) and checks that a user account icon (with aria-label="User Account") appears respectively.

### Cypress Testing for UI Responsiveness (Media Query CSS formatting): (Folder: frontend)
Navigate to root folder then run:
```
npm install --save-dev cypress
npm install --save-dev typescript
```
In a new terminal run(Folder: NYT-REPLICA-MAIN):
```
docker compose -f docker-compose.dev.yml up --build

docker compose -f docker-compose.prod.yml up --build
```
Go back to first terminal and navigate to frontend then run(Folder: frontend):
```
npx cypress run --spec "cypress/e2e/**/*.cy.ts"
```
The 3 unit tests demonstrate whether or not the column formatting is reponsive according to the media query specs. It does so by simulating different pixel sizes using `cy.viewport`
 citation : [Cypress](https://docs.cypress.io/app/end-to-end-testing/writing-your-first-end-to-end-test)

The following code is to address some dependency issues that could come up:
```
npm install --save-dev @testing-library/svelte
reference: https://www.npmjs.com/package/@testing-library/svelte
```
This package mainly for "render(App)" in this unit test, which can simulate the webpage and find the element in mock website.

```
npm install jsdom
```
```
npm install --save-dev @testing-library/jest-dom
```
Since when I simulate the website, I got an error as document not define. Then I search on google trying to debug. This will make Svelte simulated API to support DOM operations when using jsdom as the default environment
reference: https://github.com/sveltejs/svelte/issues/11394

```
npx run test
```

citation: [vitest](https://vitest.dev/api/vi.html#vi-stubglobal), [vi.waitFor](https://vitest.dev/api/vi.html#vi-spyon)
