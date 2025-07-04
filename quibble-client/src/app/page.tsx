import Image from 'next/image'
import { IntroHeader, IntroHero } from '@/components/Intro';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[linear-gradient(135deg,_#EEEEEE_35%,_#8A77FF_100%)] flex flex-col">
      <IntroHeader />
      <div className="flex flex-1 items-center justify-between px-16 relative">
        <IntroHero />
        <div className="absolute bottom-0 right-20 h-full w-1/2">
          <Image
            src="/assets/images/Hero_Robot.png"
            alt="Quibble Bot"
            width={400}
            height={480}
            className="h-full w-full"
            priority
          />
        </div>
      </div>
      {/* Add floating icons, SVGs, or extra graphics here if needed */}
    </main>
  )
}
