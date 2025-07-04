export default function Home() {
  return (
    <div style={{ padding: 20, fontFamily: 'Arial, sans-serif' }}>
      <h1>Привет, Next.js!</h1>
      <p>кинь полтос на карту 4441111130004470</p>
      <button
        onClick={() => alert('спс!')}
        style={{
          padding: '10px 20px',
          backgroundColor: '#0070f3',
          color: 'white',
          border: 'none',
          borderRadius: 5,
          cursor: 'pointer',
        }}
      >
        Нажми меня
      </button>
    </div>
  )
}