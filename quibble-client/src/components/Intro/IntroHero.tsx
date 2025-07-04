import IntroButton from './IntroButton';

export default function IntroHero() {
  return (
    <section className="px-8 pt-10 flex flex-col gap-6 max-w-2xl">
      <h1 className="text-5xl font-bold text-indigo-500 leading-tight mb-2">
        CREATE. ENGAGE. <span className="text-indigo-400">GROW.</span>
      </h1>
      <div className="ml-12">
        <p className="text-xl text-black mb-4">
          Experience the ease of automated content creation and keep your social media fresh.
        </p>
        <IntroButton />
      </div>
      
    </section>
  )
}
