export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function register(body: {
  username: string
  email: string
  dateOfBirth: string
  password: string
}) {
  const res = await fetch(`${API_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error((await res.json()).detail ?? 'Registration failed')
}


export async function login(username: string, password: string) {
  const res = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) throw new Error('Invalid credentials')
  return res.json() as Promise<{ access_token: string; token_type: string }>
}
