# Next.js Portfolio Migration Plan

## Overview
Migrate the static GitHub Pages portfolio site to a modern Next.js 15+ application with React 19+, TypeScript, and Tailwind CSS. The site will be configured as a dynamic Next.js app for local development with the ability to add server-side features later.

## Current Site Analysis
- **Structure**: Single-page portfolio with 5 sections (Hero, About, Projects, Contact, Footer)
- **Tech**: HTML/CSS/JS, Tailwind CSS via CDN, Font Awesome icons, vanilla JavaScript
- **Content**: 3 placeholder projects, 8 skill badges, 3 contact methods
- **Features**: Mobile menu, smooth scrolling, active nav highlighting, fade-in animations

## Content to Migrate
- **Name**: Sean Reed
- **Tagline**: "Software Developer passionate about building elegant solutions to complex problems"
- **Bio**: "I write picture books for kids about science and technology-related themes. Sometimes I also write code." + "Note: I do not look like this." (regarding GitHub avatar)
- **Skills**: Python, JavaScript, React, Node.js, TypeScript, PostgreSQL, Git, Docker
- **GitHub**: https://github.com/seanreed1111 (@seanreed1111)
- **Avatar**: https://avatars.githubusercontent.com/u/5740286?v=4
- **Email**: your.email@example.com (⚠️ placeholder in old site - will be kept as-is)
- **LinkedIn**: https://linkedin.com/in/your-profile (⚠️ placeholder in old site - will be kept as-is)
- **Projects**:
  1. E-commerce Platform (React, Node.js, PostgreSQL) - "A full-featured e-commerce platform with product management, shopping cart, and secure payment integration."
  2. Task Management App (TypeScript, React, MongoDB) - "A collaborative task management application with real-time updates, drag-and-drop functionality, and team collaboration features."
  3. Data Visualization Dashboard (Python, D3.js, Flask) - "An interactive analytics dashboard for visualizing complex datasets with customizable charts, filters, and export capabilities."

**Note**: The email and LinkedIn URLs in the old site are placeholders. These will be migrated as-is and can be updated in the data files after implementation.

## Migration Strategy

### Project Setup
1. Initialize Next.js 15+ with TypeScript and Tailwind CSS
2. Pin Node.js (v22) and pnpm (v10) with Volta
3. Install dependencies: `clsx`, `tailwind-merge`, `react-icons`
4. Configure Next.js for dynamic development (default config, no static export)

### Architecture

**Project Structure:**
```
my-project-site/
├── app/
│   ├── layout.tsx              # Root layout with metadata
│   ├── page.tsx                # Main portfolio page
│   └── globals.css             # Tailwind + custom styles
├── components/
│   ├── layout/                 # Navigation, MobileMenu, Footer
│   ├── sections/               # Hero, About, Projects, Contact
│   └── ui/                     # Reusable components (Button, Cards, etc.)
├── hooks/                      # Custom React hooks
│   ├── useScrollPosition.ts
│   ├── useActiveSection.ts
│   ├── useIntersectionObserver.ts
│   └── useMobileMenu.ts
├── types/                      # TypeScript definitions
├── data/                       # Content (projects, skills, contacts)
├── lib/                        # Utilities (cn, scrollToSection)
└── public/images/              # Static assets
```

**Key Components:**
- **Navigation**: Sticky nav with scroll-based styling, active section highlighting
- **MobileMenu**: Slide-in menu with backdrop, keyboard support
- **HeroSection**: Landing with gradient background and CTAs
- **AboutSection**: Bio and skill badges with staggered fade-in
- **ProjectsSection**: Grid of project cards with hover effects
- **ContactSection**: Contact method cards with icons
- **Footer**: Social links and copyright

**TypeScript Types:**
- `Project`: id, title, description, technologies, imageUrl, status, URLs
- `Skill`: id, name, category, IconComponent (React Icons), proficiency
- `ContactMethod`: id, type, label, value, IconComponent (React Icons)

**Custom Hooks:**
- `useScrollPosition`: Track window scroll position
- `useActiveSection`: Determine which section is currently in view
- `useIntersectionObserver`: Generic hook for fade-in animations
- `useMobileMenu`: Manage mobile menu state and body scroll lock

**Styling:**
- Tailwind CSS (proper build integration, not CDN)
- Custom utility classes in globals.css
- `cn()` helper for conditional class merging
- Responsive design (mobile-first, md breakpoint at 768px)

**Animations:**
- Intersection Observer API for fade-in effects
- CSS transitions for hover states
- Smooth scroll with offset for fixed navigation
- Staggered delays for sequential animations

### Implementation Steps

1. **Initialize Project** (30 min)
   - Create Next.js app with TypeScript and Tailwind
   - Pin versions with Volta
   - Install additional dependencies
   - Configure Next.js, TypeScript, Tailwind

2. **Types & Data** (30 min)
   - Define TypeScript interfaces
   - Create data files with content
   - Set up utility functions and constants

3. **Custom Hooks** (45 min)
   - Build scroll tracking hooks
   - Implement intersection observer hook
   - Create mobile menu state management

4. **UI Components** (1-2 hours)
   - Button, AnimatedSection, SkillBadge
   - ProjectCard, ContactCard
   - Test styling and animations

5. **Section Components** (1-2 hours)
   - Hero, About, Projects, Contact sections
   - Integrate with data and UI components
   - Verify responsive design

6. **Layout Components** (1-2 hours)
   - Navigation with scroll effects
   - Mobile menu with transitions
   - Footer with social links

7. **Assembly** (30 min)
   - Root layout with metadata
   - Main page composition
   - Verify React Icons integration

8. **Assets & Polish** (30 min)
   - Move images to public/
   - Update personal information
   - Accessibility check

9. **Testing** (30 min)
   - Start development server (`pnpm dev`)
   - Test all features and responsive design
   - Production build test (`pnpm build && pnpm start`)

## Key Technical Decisions

**Next.js Configuration:**
- App Router (modern, future-proof)
- Dynamic site (can add API routes, server components, etc.)
- Image optimization enabled (Next.js Image component fully functional)
- Strict React mode enabled
- Development server for local viewing (`pnpm dev`)
- Production mode for deployment (`pnpm build && pnpm start`)

**TypeScript:**
- Full strict mode for type safety
- Comprehensive type definitions
- No `any` types

**State Management:**
- React hooks only (no external library)
- Local state with useState
- Custom hooks for shared logic

**Icons:**
- React Icons package (`react-icons`)
- Tree-shakeable, better bundle size
- Import specific icons as React components (e.g., `FaGithub`, `FaLinkedin`, `FaEnvelope` from `react-icons/fa`)
- Type-safe with TypeScript

**Performance:**
- Static generation (SSG)
- Tailwind purges unused CSS
- Intersection Observer for efficient animations
- Lazy loading for images below fold

## Future Extensibility

Easy to add later:
- Blog with MDX (`/app/blog/`)
- Dynamic project pages (`/app/projects/[slug]/`)
- CMS integration (Sanity, Contentful)
- API routes (contact form)
- Dark mode toggle
- Analytics

## Critical Files to Implement

1. **app/page.tsx** - Main page assembly
2. **components/layout/Navigation.tsx** - Complex navigation logic
3. **hooks/useIntersectionObserver.ts** - Core animation hook
4. **types/index.ts** - Type safety foundation
5. **lib/utils.ts** - Essential utilities (cn, scrollToSection)

## Verification

After implementation, verify:
- [ ] Development server runs (`pnpm dev`)
- [ ] Site accessible at http://localhost:3000
- [ ] All sections visible and styled correctly
- [ ] Mobile menu opens/closes smoothly
- [ ] Smooth scrolling works with offset
- [ ] Active nav highlighting updates on scroll
- [ ] Fade-in animations trigger on scroll
- [ ] Project cards show hover effects
- [ ] Contact links work correctly
- [ ] Images load and display properly
- [ ] Responsive design works (mobile, tablet, desktop)
- [ ] Production build succeeds (`pnpm build`)
- [ ] Production server runs (`pnpm start`)
- [ ] TypeScript compiles without errors
- [ ] Accessibility (keyboard nav, ARIA labels)

## Success Criteria

- Modern Next.js site with TypeScript
- Preserves all features from static site
- Clean, maintainable component architecture
- Type-safe implementation
- Responsive and accessible
- Runs locally with `pnpm dev` for development
- Production-ready build with `pnpm build && pnpm start`
- Easy to extend with server-side features (API routes, server actions, etc.)
