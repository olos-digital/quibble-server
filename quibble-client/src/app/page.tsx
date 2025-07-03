import { redirect } from 'next/navigation';

export default async function Root() {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      redirect('/community');
    } else {
      redirect('/login');
    }
    return null;
  }
  redirect('/login');
}