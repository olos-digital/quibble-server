import Image from 'next/image'

export interface Post {
    id: string
    username: string
    image: string
    title: string
    category: string
    content: string
    likes: number
    createdAt: string
}

export default function CommunityPostCard({ post }: { post: Post }) {
  return (
    <div className="rounded-xl bg-white shadow hover:shadow-lg transition overflow-hidden">
      <div className="relative h-60 w-full">
        <Image src={post.image} alt={post.title} fill className="object-cover" />
      </div>
      <div className="p-4 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="font-bold text-indigo-600">@{post.username}</span>
          <span className="text-xs text-gray-400">{post.createdAt}</span>
        </div>
        <h3 className="font-semibold">{post.title}</h3>
        <p className="text-sm text-gray-700 line-clamp-2">{post.content}</p>
        <div className="flex items-center gap-2 pt-2">
          <span className="text-rose-500">♥</span>
          <span className="text-xs">{post.likes}</span>
        </div>
      </div>
    </div>
  )
}