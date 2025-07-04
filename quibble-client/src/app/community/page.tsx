import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default function CommunityPage() {
  const token = localStorage.getItem('access_token');
  if (!token) redirect('/login')

  return (
    <main className="flex h-screen items-center justify-center">
      <h1 className="text-3xl font-semibold">Community – coming soon</h1>
    </main>
  )
}
