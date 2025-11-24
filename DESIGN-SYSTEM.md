# 🎨 Design System & Theme Guide

## Overview

This design system defines the visual language and component patterns used throughout the HR SaaS application. It ensures consistency, professionalism, and a modern user experience across all pages.

---

## 🎨 Color Palette

### Primary Colors

```css
/* Blue - Primary Brand Color */
--blue-50:  #eff6ff
--blue-100: #dbeafe
--blue-500: #3b82f6  /* Primary */
--blue-600: #2563eb  /* Primary Dark */
--blue-700: #1d4ed8  /* Primary Darker */

/* Indigo - Secondary Brand Color */
--indigo-500: #6366f1  /* Secondary */
--indigo-600: #4f46e5  /* Secondary Dark */
--indigo-700: #4338ca  /* Secondary Darker */

/* Purple - Tertiary Accent */
--purple-500: #8b5cf6
--purple-600: #7c3aed
```

### Gradient Combinations

```tsx
// Primary Brand Gradient
className="bg-gradient-to-r from-blue-600 to-indigo-600"

// Light Gradient
className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50"

// Dark Gradient
className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900"

// Button Hover Gradient
className="bg-gradient-to-r from-blue-700 to-indigo-700"
```

### Accent Colors

```css
/* Success / Green */
--green-300: #86efac
--green-500: #10b981
--green-600: #059669

/* Warning / Orange */
--orange-500: #f59e0b
--orange-600: #d97706

/* Error / Red */
--red-500: #ef4444
--red-600: #dc2626

/* Info / Cyan */
--cyan-500: #06b6d4
--cyan-600: #0891b2

/* Pink Accent */
--pink-500: #ec4899
--pink-600: #db2777
```

### Neutral Scale

```css
/* Gray Scale - Use for text and backgrounds */
--gray-50:  #f9fafb  /* Lightest background */
--gray-100: #f3f4f6  /* Light background */
--gray-200: #e5e7eb  /* Borders */
--gray-300: #d1d5db  /* Disabled */
--gray-400: #9ca3af  /* Placeholder */
--gray-500: #6b7280  /* Secondary text */
--gray-600: #4b5563  /* Body text */
--gray-700: #374151  /* Primary text */
--gray-800: #1f2937  /* Headings */
--gray-900: #111827  /* Strong headings */
```

---

## 📝 Typography

### Font Family

```css
/* Default Next.js font optimization */
font-family: system-ui, -apple-system, sans-serif;
```

### Type Scale

```tsx
// Headings
"text-8xl"  // 96px - Hero headlines
"text-7xl"  // 72px - Main hero
"text-6xl"  // 60px - Section headers
"text-5xl"  // 48px - Page titles
"text-4xl"  // 36px - Card titles
"text-3xl"  // 30px - Subsection titles
"text-2xl"  // 24px - Large text
"text-xl"   // 20px - Lead paragraphs

// Body
"text-lg"   // 18px - Large body
"text-base" // 16px - Standard body
"text-sm"   // 14px - Small text
"text-xs"   // 12px - Captions
```

### Font Weights

```tsx
"font-bold"      // 700 - Headlines, CTAs
"font-semibold"  // 600 - Subheadings
"font-medium"    // 500 - Labels, buttons
"font-normal"    // 400 - Body text
```

### Text Colors

```tsx
// Headings
"text-gray-900"  // Primary headings
"text-gray-800"  // Secondary headings

// Body text
"text-gray-700"  // Primary body
"text-gray-600"  // Secondary body
"text-gray-500"  // Tertiary/muted

// Special
"text-blue-600"  // Links, interactive
"bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"  // Gradient text
```

### Line Heights

```tsx
"leading-tight"    // 1.25 - Headings
"leading-relaxed"  // 1.625 - Body text
"leading-loose"    // 2.0 - Spacious text
```

---

## 📐 Spacing System

### Container Widths

```tsx
"max-w-7xl"  // 1280px - Main content container
"max-w-6xl"  // 1152px - Narrow content
"max-w-5xl"  // 1024px - Form containers
"max-w-4xl"  // 896px - Article width
"max-w-3xl"  // 768px - Readable text
```

### Section Padding

```tsx
// Vertical spacing
"py-24"  // 96px - Main sections
"py-16"  // 64px - Subsections
"py-12"  // 48px - Card groups
"py-8"   // 32px - Cards
"py-6"   // 24px - Small sections
"py-4"   // 16px - Tight sections

// Horizontal spacing
"px-6"   // 24px - Container padding
"px-4"   // 16px - Mobile padding
```

### Element Spacing

```tsx
// Gaps between elements
"gap-12"  // 48px - Large gaps
"gap-8"   // 32px - Medium gaps
"gap-6"   // 24px - Standard gaps
"gap-4"   // 16px - Small gaps
"gap-3"   // 12px - Tight gaps
"gap-2"   // 8px - Very tight gaps

// Margin bottom (stacking)
"mb-16"   // 64px - Section spacing
"mb-12"   // 48px - Large spacing
"mb-8"    // 32px - Medium spacing
"mb-6"    // 24px - Standard spacing
"mb-4"    // 16px - Small spacing
```

---

## 🎭 Component Patterns

### Buttons

#### Primary Button
```tsx
<Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300">
  Click Me
</Button>
```

#### Secondary Button
```tsx
<Button variant="outline" className="bg-white hover:bg-gray-50 shadow-md hover:shadow-lg transform hover:scale-105 transition-all duration-300">
  Learn More
</Button>
```

#### Ghost Button
```tsx
<Button variant="ghost" className="hover:bg-gray-100 transition-colors">
  Cancel
</Button>
```

### Cards

#### Standard Card
```tsx
<Card className="p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border-0 bg-white">
  {/* Content */}
</Card>
```

#### Interactive Card (with hover lift)
```tsx
<Card className="p-8 shadow-xl hover:shadow-2xl transition-all duration-300 group cursor-pointer hover:-translate-y-2">
  {/* Content */}
</Card>
```

#### Card with Gradient Border
```tsx
<div className="bg-gradient-to-r from-blue-500 to-indigo-600 p-1 rounded-3xl shadow-2xl">
  <Card className="bg-white rounded-3xl p-8">
    {/* Content */}
  </Card>
</div>
```

### Badges

#### Status Badge
```tsx
<span className="px-3 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
  Active
</span>
```

#### Info Badge
```tsx
<div className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full shadow-lg border border-blue-100">
  <span className="text-sm font-medium text-gray-700">New Feature</span>
</div>
```

### Icons

#### Icon Container
```tsx
<div className="inline-flex p-4 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600">
  <Icon className="h-8 w-8 text-white" />
</div>
```

#### Icon with Hover Effect
```tsx
<motion.div
  whileHover={{ scale: 1.1, rotate: 5 }}
  className="inline-flex p-4 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600"
>
  <Icon className="h-8 w-8 text-white" />
</motion.div>
```

---

## ✨ Effects & Shadows

### Shadow Scale

```tsx
// Elevations
"shadow-sm"   // Subtle depth
"shadow"      // Standard depth
"shadow-md"   // Medium depth
"shadow-lg"   // Large depth
"shadow-xl"   // Extra large depth
"shadow-2xl"  // Maximum depth

// Hover states (always increase shadow on hover)
"shadow-lg hover:shadow-xl"
"shadow-xl hover:shadow-2xl"
```

### Glass Morphism

```tsx
// Light glass effect
"bg-white/80 backdrop-blur-sm"

// Medium glass effect
"bg-white/70 backdrop-blur-md"

// Strong glass effect
"bg-white/60 backdrop-blur-lg"
```

### Border Radius

```tsx
// Scale
"rounded-sm"    // 2px - Minimal
"rounded"       // 4px - Subtle
"rounded-md"    // 6px - Standard
"rounded-lg"    // 8px - Medium
"rounded-xl"    // 12px - Large
"rounded-2xl"   // 16px - Extra large
"rounded-3xl"   // 24px - Maximum
"rounded-full"  // 9999px - Pills, circles
```

---

## 🎬 Animation Guidelines

### Timing Functions

```tsx
// Standard transitions
"transition-all duration-300"      // Quick interactions
"transition-all duration-500"      // Standard animations
"transition-all duration-700"      // Smooth entrances

// Easing
"ease-in"        // Starts slow
"ease-out"       // Ends slow
"ease-in-out"    // Smooth both ends (recommended)
```

### Common Animations

#### Hover Scale
```tsx
"transform hover:scale-105 transition-transform duration-300"
```

#### Hover Lift
```tsx
"hover:-translate-y-2 transition-all duration-300"
```

#### Fade In (Framer Motion)
```tsx
initial={{ opacity: 0, y: 20 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.6 }}
```

#### Staggered Children
```tsx
// Parent
initial={{ opacity: 0 }}
animate={{ opacity: 1 }}

// Children
transition={{ delay: index * 0.1, duration: 0.5 }}
```

#### Hover Effects
```tsx
whileHover={{ scale: 1.05 }}
transition={{ type: "spring", stiffness: 300 }}
```

### Animation Durations

```
Quick:    0.15s - 0.3s  (micro-interactions)
Standard: 0.3s - 0.6s   (UI transitions)
Smooth:   0.6s - 1.0s   (page entrances)
Slow:     8s - 12s      (ambient animations)
```

---

## 📱 Responsive Design

### Breakpoints

```tsx
// Mobile first approach
"sm:"   // 640px  - Small tablets
"md:"   // 768px  - Tablets
"lg:"   // 1024px - Desktops
"xl:"   // 1280px - Large desktops
"2xl:"  // 1536px - Extra large screens
```

### Grid Patterns

#### Responsive Grid
```tsx
"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
```

#### Auto-fit Grid
```tsx
"grid grid-cols-[repeat(auto-fit,minmax(300px,1fr))] gap-6"
```

### Mobile Optimizations

```tsx
// Hide on mobile
"hidden md:flex"

// Stack on mobile
"flex-col md:flex-row"

// Smaller text on mobile
"text-4xl md:text-6xl"

// Reduced padding on mobile
"px-4 md:px-6 lg:px-8"
```

---

## 🎯 Layout Patterns

### Hero Section Layout

```tsx
<section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden">
  {/* Background */}
  <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
    {/* Decorative elements */}
  </div>
  
  {/* Content */}
  <div className="relative max-w-7xl mx-auto px-6 py-24 text-center">
    {/* Hero content */}
  </div>
</section>
```

### Section Layout

```tsx
<section className="py-24 bg-white">
  <div className="max-w-7xl mx-auto px-6">
    {/* Section header */}
    <div className="text-center mb-16">
      <h2 className="text-5xl font-bold mb-4">Section Title</h2>
      <p className="text-xl text-gray-600">Description</p>
    </div>
    
    {/* Section content */}
    <div className="grid md:grid-cols-3 gap-8">
      {/* Cards or content */}
    </div>
  </div>
</section>
```

### Two-Column Layout

```tsx
<div className="grid md:grid-cols-2 gap-12 items-center">
  <div className="space-y-6">
    {/* Text content */}
  </div>
  <div>
    {/* Image or visual */}
  </div>
</div>
```

---

## 🎨 Gradient Library

### Background Gradients

```tsx
// Subtle backgrounds
"bg-gradient-to-b from-white to-gray-50"
"bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50"

// Bold backgrounds
"bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700"
"bg-gradient-to-r from-blue-600 to-indigo-600"

// Dark gradients
"bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900"
```

### Text Gradients

```tsx
"bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"
"bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent"
"bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent"
```

### Button Gradients

```tsx
// Primary
"bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"

// Success
"bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"

// Warning
"bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700"
```

---

## 🏗️ Form Styling

### Input Fields

```tsx
<Input className="border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all" />
```

### Select Dropdowns

```tsx
<select className="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all">
  <option>Option</option>
</select>
```

### Form Layout

```tsx
<form className="space-y-6">
  <div>
    <Label className="text-sm font-medium text-gray-700">Field Label</Label>
    <Input className="mt-1" />
  </div>
  
  <div className="flex gap-3">
    <Button type="submit">Submit</Button>
    <Button type="button" variant="outline">Cancel</Button>
  </div>
</form>
```

---

## 📊 Data Visualization

### Status Indicators

```tsx
// Success
<span className="inline-flex h-2 w-2 rounded-full bg-green-500"></span>

// Warning
<span className="inline-flex h-2 w-2 rounded-full bg-orange-500"></span>

// Error
<span className="inline-flex h-2 w-2 rounded-full bg-red-500"></span>

// With pulse
<span className="relative flex h-3 w-3">
  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
  <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
</span>
```

### Progress Bars

```tsx
<div className="w-full bg-gray-100 rounded-full h-2">
  <div 
    className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full transition-all"
    style={{ width: `${percentage}%` }}
  />
</div>
```

---

## 🎯 Best Practices

### 1. Consistency Rules

- ✅ Always use the defined color palette
- ✅ Use spacing scale consistently (4, 6, 8, 12, 16, 24)
- ✅ Maintain consistent border radius across similar elements
- ✅ Use shadows to establish hierarchy
- ✅ Apply hover states to all interactive elements

### 2. Gradient Usage

- Use gradients for **CTAs** and **hero sections**
- Use **subtle gradients** for backgrounds
- Use **text gradients** for emphasis, not body text
- Always provide hover states for gradient buttons

### 3. Animation Guidelines

- ✅ Keep animations under 1 second for UI interactions
- ✅ Use easing functions for natural motion
- ✅ Provide feedback for all user actions
- ❌ Don't animate on every element (causes distraction)
- ❌ Don't use auto-play animations excessively

### 4. Accessibility

- Maintain 4.5:1 contrast ratio for body text
- Maintain 3:1 contrast ratio for large text
- Provide focus states for keyboard navigation
- Include aria labels for icon buttons
- Ensure touch targets are at least 44×44px

### 5. Performance

- Use `transform` and `opacity` for animations (GPU accelerated)
- Lazy load images and heavy components
- Use `viewport={{ once: true }}` for scroll animations
- Optimize gradient usage (can be heavy)

---

## 📦 Component Checklist

When creating new components, ensure:

- [ ] Uses colors from the palette
- [ ] Has consistent spacing
- [ ] Includes hover states
- [ ] Has proper shadow depth
- [ ] Is fully responsive
- [ ] Includes loading states
- [ ] Has error states
- [ ] Uses proper typography scale
- [ ] Has smooth transitions
- [ ] Follows accessibility guidelines

---

## 🎨 Theme Extension

### Adding New Colors

When adding colors to the theme:

1. Follow the same shade structure (50-900)
2. Maintain consistency with existing palette
3. Test for accessibility
4. Document gradient combinations
5. Update this guide

### Creating New Patterns

When creating new patterns:

1. Start with existing components
2. Maintain visual consistency
3. Test across breakpoints
4. Document in this guide
5. Share with team

---

## 📚 Quick Reference

### Most Used Classes

```tsx
// Containers
"max-w-7xl mx-auto px-6 py-24"

// Cards
"bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-all duration-300"

// Buttons
"bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 py-3 rounded-lg font-medium shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"

// Headings
"text-5xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent"

// Body Text
"text-gray-600 leading-relaxed"

// Spacing
"space-y-8"  // Vertical spacing
"gap-8"      // Grid/flex gap
```

---

## 🔗 Resources

- **Tailwind CSS Docs**: https://tailwindcss.com/docs
- **Framer Motion**: https://www.framer.com/motion/
- **Lucide Icons**: https://lucide.dev/
- **Color Tools**: https://uicolors.app/create

---

**This design system ensures consistency, professionalism, and a delightful user experience across the entire HR SaaS platform.**

*Last updated: 2024*

