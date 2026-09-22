import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'
import { vi } from 'vitest'

vi.mock('./lib/api', () => ({
  api: {
    listTranscripts: vi.fn().mockResolvedValue([
      { id: '1', market: 'France', expert_name: 'Dr. Jean Martin', role: 'Head of Urology', chunk_count: 12 },
      { id: '2', market: 'Germany', expert_name: 'Anna Keller', role: 'Former Hospital Procurement Director', chunk_count: 12 },
      { id: '3', market: 'United Kingdom', expert_name: 'Dr. Emily Carter', role: 'Consultant Urologist', chunk_count: 14 },
    ]),
    analyzeGuide: vi.fn(),
    crossAnalysis: vi.fn(),
    ask: vi.fn(),
    upload: vi.fn().mockResolvedValue({}),
  },
}))


test('renders workspace overview', async () => {
  render(<App />)
  await waitFor(() => expect(screen.getByText('European Robotic Surgery Market')).toBeInTheDocument())
  expect(screen.getByText('Turn interview transcripts into evidence you can trust.')).toBeInTheDocument()
  expect(screen.getByText('France')).toBeInTheDocument()
  expect(screen.getByText('Germany')).toBeInTheDocument()
  expect(screen.getByText('United Kingdom')).toBeInTheDocument()
})


test('switches navigation to ask view', async () => {
  const user = userEvent.setup()
  render(<App />)
  await waitFor(() => screen.getByRole('button', { name: /ask the corpus/i }))
  await user.click(screen.getByRole('button', { name: /ask the corpus/i }))
  expect(screen.getByText('Ask one question across every interview.')).toBeInTheDocument()
})
