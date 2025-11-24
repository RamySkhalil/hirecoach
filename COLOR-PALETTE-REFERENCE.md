# 🎨 Color Palette Quick Reference

## Copy-Paste Ready Styles

---

## 🔵 Primary Colors (Blue/Indigo)

### Gradient Backgrounds
```tsx
// Primary Button
className="bg-gradient-to-r from-blue-600 to-indigo-600"

// Hover State
className="hover:from-blue-700 hover:to-indigo-700"

// Light Background
className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50"

// Hero Background
className="bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700"
```

### Gradient Text
```tsx
// Primary Heading
className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"

// Dark Heading
className="bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent"
```

### Solid Colors
```tsx
// Text
"text-blue-600"    // Links, interactive
"text-blue-700"    // Darker links
"text-indigo-600"  // Alternative

// Backgrounds
"bg-blue-50"       // Very light
"bg-blue-100"      // Light
"bg-blue-600"      // Primary
```

---

## 🟢 Success (Green)

### Status Badges
```tsx
// Success Badge
className="px-3 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800"

// Active Status Dot
className="h-2 w-2 rounded-full bg-green-500"

// Success Button
className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"
```

### Colors
```tsx
"text-green-600"   // Success text
"text-green-700"   // Darker success
"bg-green-50"      // Light background
"bg-green-100"     // Badge background
"border-green-500" // Border
```

---

## 🟠 Warning (Orange)

### Status Badges
```tsx
// Warning Badge
className="px-3 py-1 text-xs font-medium rounded-full bg-orange-100 text-orange-800"

// Pending Badge
className="px-3 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800"
```

### Colors
```tsx
"text-orange-600"  // Warning text
"bg-orange-50"     // Light background
"bg-orange-100"    // Badge background
"border-orange-500" // Border
```

---

## 🔴 Error/Danger (Red)

### Buttons & Alerts
```tsx
// Delete Button
className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"

// Error Badge
className="px-3 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800"

// Error Message
className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800"
```

### Colors
```tsx
"text-red-600"     // Error text
"text-red-700"     // Darker error
"bg-red-50"        // Light background
"bg-red-100"       // Badge background
"border-red-500"   // Border
```

---

## ⚫ Neutral (Gray)

### Text Hierarchy
```tsx
// Headings
"text-gray-900"    // Primary headings (darkest)
"text-gray-800"    // Secondary headings

// Body Text
"text-gray-700"    // Primary body text
"text-gray-600"    // Secondary body text
"text-gray-500"    // Tertiary/muted text
"text-gray-400"    // Placeholder text
```

### Backgrounds
```tsx
"bg-white"         // Main background
"bg-gray-50"       // Subtle background
"bg-gray-100"      // Light background
"bg-gray-200"      // Medium background
"bg-gray-800"      // Dark background
"bg-gray-900"      // Darkest background
```

### Borders
```tsx
"border-gray-100"  // Very subtle
"border-gray-200"  // Standard
"border-gray-300"  // Medium
```

---

## 🎨 Accent Colors

### Purple
```tsx
// Badge
className="px-3 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800"

// Button
className="bg-gradient-to-r from-purple-500 to-purple-600"

// Text
"text-purple-600"
"bg-purple-50"
```

### Pink
```tsx
// Badge
className="px-3 py-1 text-xs font-medium rounded-full bg-pink-100 text-pink-800"

// Gradient
className="bg-gradient-to-r from-pink-500 to-rose-600"

// Text
"text-pink-600"
"bg-pink-50"
```

### Cyan
```tsx
// Badge
className="px-3 py-1 text-xs font-medium rounded-full bg-cyan-100 text-cyan-800"

// Button
className="bg-gradient-to-r from-cyan-500 to-blue-600"

// Text
"text-cyan-600"
"bg-cyan-50"
```

---

## 📦 Common Component Styles

### Primary Button
```tsx
className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 py-3 rounded-lg font-medium shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
```

### Secondary Button
```tsx
className="bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 px-6 py-3 rounded-lg font-medium shadow-md hover:shadow-lg transform hover:scale-105 transition-all duration-300"
```

### Card
```tsx
className="bg-white rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border-0 p-8"
```

### Card with Hover Lift
```tsx
className="bg-white rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border-0 p-8 hover:-translate-y-2 cursor-pointer group"
```

### Input Field
```tsx
className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none"
```

### Badge (Generic)
```tsx
className="px-3 py-1 text-xs font-medium rounded-full"

// Then add specific colors:
// Success: bg-green-100 text-green-800
// Warning: bg-orange-100 text-orange-800
// Error: bg-red-100 text-red-800
// Info: bg-blue-100 text-blue-800
// Neutral: bg-gray-100 text-gray-800
```

---

## 🎯 Status Color Guide

```tsx
// Open/Active
className="bg-green-100 text-green-800"

// Pending/In Progress
className="bg-yellow-100 text-yellow-800"

// Closed/Inactive
className="bg-gray-100 text-gray-800"

// Draft
className="bg-blue-100 text-blue-800"

// Error/Failed
className="bg-red-100 text-red-800"

// Archived
className="bg-purple-100 text-purple-800"
```

---

## 🎨 Gradient Collection

### Button Gradients
```tsx
// Primary
"from-blue-600 to-indigo-600"

// Success
"from-green-500 to-emerald-600"

// Warning
"from-orange-500 to-red-600"

// Info
"from-cyan-500 to-blue-600"

// Secondary
"from-purple-500 to-pink-600"
```

### Background Gradients
```tsx
// Subtle Light
"from-gray-50 to-white"
"from-blue-50 via-indigo-50 to-purple-50"

// Bold
"from-blue-600 via-indigo-600 to-purple-700"
"from-blue-600 to-indigo-600"

// Dark
"from-gray-900 via-gray-800 to-gray-900"
```

### Text Gradients
```tsx
// Heading
"from-gray-900 to-gray-700"

// Primary Brand
"from-blue-600 to-indigo-600"

// Accent
"from-purple-600 to-pink-600"
```

---

## 🔢 Opacity Scale

```tsx
// Backgrounds with transparency
"bg-white/80"      // 80% opacity
"bg-white/70"      // 70% opacity
"bg-white/60"      // 60% opacity
"bg-black/50"      // 50% opacity
"bg-blue-600/20"   // 20% opacity (subtle tints)
```

---

## 🎭 Shadow Scale

```tsx
"shadow-sm"        // Subtle
"shadow"           // Default
"shadow-md"        // Medium
"shadow-lg"        // Large
"shadow-xl"        // Extra large
"shadow-2xl"       // Maximum

// Hover progressions
"shadow-lg hover:shadow-xl"
"shadow-xl hover:shadow-2xl"
```

---

## 🎨 Icon Container Styles

### Standard Icon Container
```tsx
<div className="inline-flex p-4 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600">
  <Icon className="h-8 w-8 text-white" />
</div>
```

### Hover Effect
```tsx
<motion.div
  whileHover={{ scale: 1.1, rotate: 5 }}
  className="inline-flex p-4 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600"
>
  <Icon className="h-8 w-8 text-white" />
</motion.div>
```

---

## 📊 Data Visualization Colors

Use for charts and graphs:

```tsx
const CHART_COLORS = [
  '#3b82f6',  // Blue
  '#10b981',  // Green
  '#f59e0b',  // Orange
  '#ef4444',  // Red
  '#8b5cf6',  // Purple
  '#ec4899',  // Pink
  '#06b6d4',  // Cyan
  '#f97316',  // Orange-red
]
```

---

## 🔄 Interactive States

### Hover States
```tsx
// Text
"hover:text-blue-600"

// Background
"hover:bg-gray-50"
"hover:bg-blue-600"

// Shadow
"hover:shadow-xl"

// Transform
"hover:scale-105"
"hover:-translate-y-2"
```

### Focus States
```tsx
// Inputs
"focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"

// Buttons
"focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
```

### Active States
```tsx
"active:scale-95"
"active:shadow-inner"
```

### Disabled States
```tsx
"disabled:opacity-50"
"disabled:cursor-not-allowed"
"disabled:bg-gray-100"
```

---

## 💡 Usage Tips

1. **Always pair gradients with hover states**
   ```tsx
   from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700
   ```

2. **Add transitions to interactive elements**
   ```tsx
   transition-all duration-300
   ```

3. **Combine shadow with scale on hover**
   ```tsx
   shadow-lg hover:shadow-xl hover:scale-105
   ```

4. **Use glass morphism for overlays**
   ```tsx
   bg-white/80 backdrop-blur-lg
   ```

5. **Maintain text contrast**
   - Dark text (700-900) on light backgrounds
   - Light text (white) on dark backgrounds
   - Check contrast ratios for accessibility

---

## 📋 Quick Copy Templates

### Page Header
```tsx
<div className="mb-12">
  <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-3">
    Page Title
  </h1>
  <p className="text-xl text-gray-600">
    Description text
  </p>
</div>
```

### Stat Card
```tsx
<Card className="border-0 shadow-xl bg-gradient-to-br from-blue-50 to-indigo-50 p-6">
  <p className="text-sm font-medium text-gray-600">Label</p>
  <p className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mt-2">
    127
  </p>
</Card>
```

### Action Button
```tsx
<Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300">
  Action
</Button>
```

---

**Save this for quick reference when building components!**

