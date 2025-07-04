import Link from 'next/link';

export default function IntroButton() {
  return (
    <Link href="/community">
      <button className="flex items-center px-8 py-3 rounded-full bg-indigo-500 text-white font-bold text-lg shadow-lg hover:bg-indigo-600 transition gap-4 align-middle vertical-align-middle">
        CREATE POSTS
        <span className="material-icons">
          <img src="assets/icons/action.svg" alt="Action" width={22} height={22} />
        </span>
      </button>
    </Link>
  )
}
