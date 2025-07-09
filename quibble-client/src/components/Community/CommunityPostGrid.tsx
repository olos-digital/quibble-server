import { CommunityPostCard, Post } from ".";

export default function CommunityPostGrid({ posts }: { posts: Post[] }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
      {posts.map(post => (
        <CommunityPostCard key={post.id} post={post} />
      ))}
    </div>
  )
}