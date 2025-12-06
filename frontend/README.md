# Interviewly Frontend

Next.js 14+ frontend for the Interviewly AI Interview Coach platform.

## Features

- **Modern UI**: Beautiful, gradient-based design using Tailwind CSS
- **Smooth Animations**: Powered by Framer Motion
- **Responsive Design**: Mobile-first approach, works on all devices
- **Type-Safe**: Full TypeScript implementation
- **API Integration**: Clean API client for backend communication

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **State Management**: React hooks

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx                           # Landing page
│   ├── layout.tsx                         # Root layout with navbar
│   ├── globals.css                        # Global styles
│   ├── interview/
│   │   ├── setup/
│   │   │   └── page.tsx                   # Interview setup form
│   │   ├── session/
│   │   │   └── [sessionId]/
│   │   │       └── page.tsx               # Interview session room
│   │   └── report/
│   │       └── [sessionId]/
│   │           └── page.tsx               # Final report page
├── components/
│   └── Navbar.tsx                         # Navigation bar
├── lib/
│   ├── api.ts                             # API client functions
│   └── utils.ts                           # Utility functions
├── public/                                # Static assets
├── package.json
└── tsconfig.json
```

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env.local` file (copy from `env.local.example`):

```bash
# Windows
copy env.local.example .env.local

# Mac/Linux
cp env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at: `http://localhost:3000`

## Available Scripts

```bash
# Development
npm run dev          # Start dev server with hot reload

# Production
npm run build        # Build for production
npm run start        # Start production server

# Linting
npm run lint         # Run ESLint
```

## Pages Overview

### Landing Page (`/`)

- Hero section with CTA
- Features showcase
- How it works section
- Footer

### Setup Page (`/interview/setup`)

- Job title input
- Seniority level selection (Junior/Mid/Senior)
- Language selection (English/Arabic)
- Number of questions selector
- Creates new interview session

### Session Page (`/interview/session/[sessionId]`)

- Displays current question
- Progress bar
- Text input for answers
- Instant feedback after submission
- Dimensional scoring display
- Coach notes
- Auto-navigation to next question or report

### Report Page (`/interview/report/[sessionId]`)

- Overall score visualization
- Strengths and weaknesses
- Personalized action plan
- Suggested roles
- CTAs to start new interview

## Design System

The frontend follows the design system defined in `DESIGN-SYSTEM.md`:

### Colors

- **Primary**: Blue (#3b82f6) to Indigo (#4f46e5) gradient
- **Success**: Green (#10b981)
- **Warning**: Orange (#f59e0b)
- **Error**: Red (#ef4444)

### Components

- **Buttons**: Gradient backgrounds with hover effects
- **Cards**: Shadow-xl with hover lift animation
- **Forms**: Focus rings with transition effects
- **Badges**: Rounded-full with appropriate colors

### Animations

- Page transitions: Fade in + slide up
- Hover effects: Scale transform
- Loading states: Spinner animations
- Progress bars: Smooth width transitions

## API Integration

The frontend communicates with the FastAPI backend through functions in `lib/api.ts`:

```typescript
// Start interview
const response = await startInterview({
  job_title: "Software Engineer",
  seniority: "mid",
  language: "en",
  num_questions: 5
});

// Submit answer
const feedback = await submitAnswer({
  session_id: sessionId,
  question_id: questionId,
  user_answer_text: answer
});

// Get final report
const report = await finishInterview(sessionId);
```

## State Management

Uses React hooks for state:

- `useState` for component state
- `useEffect` for data fetching
- `useRouter` for navigation
- `useParams` for route parameters

## Responsive Design

Breakpoints (Tailwind):
- `sm`: 640px (tablets)
- `md`: 768px (small laptops)
- `lg`: 1024px (desktops)
- `xl`: 1280px (large desktops)

Example usage:
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

## Customization

### Changing Colors

Edit Tailwind classes in components or extend `tailwind.config.ts`:

```ts
theme: {
  extend: {
    colors: {
      primary: '#your-color',
    }
  }
}
```

### Adding New Pages

1. Create file in `app/` directory following Next.js App Router conventions
2. Use TypeScript and include proper types
3. Follow design system patterns
4. Add animation with Framer Motion

### Custom Components

Place reusable components in `components/` directory and import as needed.

## Error Handling

All API calls include try-catch blocks with user-friendly error messages:

```typescript
try {
  const data = await apiCall();
} catch (err: any) {
  setError(err.message || "Something went wrong");
}
```

## Loading States

Loading states use:
- Loader2 icon with spin animation
- Disabled buttons with visual feedback
- Skeleton screens (can be added)

## Future Enhancements

- [ ] Voice recording (STT integration)
- [ ] Avatar video display
- [ ] Real-time feedback during typing
- [ ] Interview history dashboard
- [ ] User authentication
- [ ] Dark mode support
- [ ] Multi-language support
- [ ] Analytics dashboard

## Performance Optimization

- Server Components where possible
- Client Components only when needed
- Image optimization with Next.js Image
- Code splitting automatic with App Router
- CSS optimization with Tailwind purge

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
npx kill-port 3000

# Or use different port
npm run dev -- -p 3001
```

### API Connection Issues

- Ensure backend is running on `http://localhost:8000`
- Check CORS configuration in backend
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

### Build Errors

```bash
# Clear cache
rm -rf .next
npm run build
```

## Contributing

1. Follow TypeScript best practices
2. Use functional components with hooks
3. Include proper types for all props
4. Follow design system guidelines
5. Test on multiple screen sizes

## License

Proprietary - All rights reserved
