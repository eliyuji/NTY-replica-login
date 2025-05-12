import { writable } from 'svelte/store';

export interface User {
  email: string;
  exp: number;
}

function decodeToken(token: string): User | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return {
      email: payload.email,
      exp: payload.exp
    };
  } catch (e) {
    return null;
  }
}

const storedToken = localStorage.getItem('id_token');
const initialUser = storedToken ? decodeToken(storedToken) : null;

export const user = writable<User | null>(initialUser);

export function logout() {
  localStorage.removeItem('id_token');
  user.set(null);
}
