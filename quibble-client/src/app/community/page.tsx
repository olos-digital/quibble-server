'use client'

import { CommunityHeader, CommunityPostGrid, CommunitySidebar, CommunitySortBar } from '@/components/Community';
import { Post } from '@/components/Community/CommunityPostCard';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function CommunityPage() {
    const router = useRouter();
    const [checking, setChecking] = useState(true);
    const [selectedFilter, setSelectedFilter] = useState('all');

    const posts: Post[] = [];

    const filteredPosts = posts.filter(post => selectedFilter === 'all' || post.category === selectedFilter)

    useEffect(() => {
      const token = localStorage.getItem('access_token')
      if (!token) {
        router.replace('/login')
      } else {
        setChecking(false)
      }
    }, [router])

    if (checking) {
      return <div className="flex h-screen items-center justify-center">Loading...</div>
  }

  return (
    <div className="min-h-screen w-full p-0 m-0 bg-gray-50 flex flex-row justify-between items-start">
        <main className="flex-2 flex flex-col gap-6">
          <CommunityHeader />
          <CommunitySortBar selected={selectedFilter} onSelect={setSelectedFilter} />
          <CommunityPostGrid posts={filteredPosts} />
        </main>
      <CommunitySidebar />
    </div>
  )
}
