# Design System Specification: The Modern Oasis

## 1. Overview & Creative North Star
The visual identity of this design system is anchored by a concept we call **"The Modern Oasis."** In the context of a marketplace for Afghanistan, we move away from the cluttered, "grid-locked" feel of traditional e-commerce. Instead, we embrace a high-end editorial aesthetic defined by **breathable luxury, intentional asymmetry, and tonal depth.**

This system rejects the "template" look. We treat the mobile screen as a digital canvas where Persian and Pashto typography are given the space to breathe. By utilizing generous whitespace (the "Oasis") and shifting away from rigid borders, we create an interface that feels less like a utility and more like a curated experience. 

**The Creative North Star:** *Sophisticated Simplicity.* We achieve this through "Soft Minimalism"—where the UI recedes to let the products and the culture take center stage, using depth and tone rather than lines to guide the eye.

---

## 2. Colors & Surface Architecture
Our palette transitions from the deep, authoritative `#17252A` (Secondary) to the refreshing, modern `#2B7A78` (Primary/Primary Container), grounded by a sophisticated `#F5F5F5` (Surface) background.

### The "No-Line" Rule
To maintain a premium, bespoke feel, **1px solid borders are strictly prohibited** for sectioning or containment. Boundaries must be defined through background color shifts. 
*   **Implementation:** Use `surface-container-low` for sections resting on a `surface` background. The shift in tone creates a natural, organic boundary that feels more integrated than a hard line.

### Surface Hierarchy & Nesting
Think of the UI as a series of physical layers—like stacked sheets of fine paper.
*   **Surface (Base):** Your foundational canvas.
*   **Surface-Container-Lowest:** Used for primary content cards (e.g., product listings) to create a subtle lift.
*   **Surface-Container-High:** Used for elevated elements like bottom sheets or floating headers.
*   **Nesting:** When placing a search bar inside a header, use a `surface-container-highest` element inside a `surface-container-low` area. This "nested depth" provides clarity without visual noise.

### The "Glass & Gradient" Rule
To elevate the experience beyond "standard" flat design:
*   **Signature Textures:** Use subtle linear gradients for main CTAs, transitioning from `primary` (#00615f) to `primary_container` (#2B7A78). This provides a "soul" to the action buttons.
*   **Glassmorphism:** For floating navigation bars or top headers, use `surface_container_lowest` at 80% opacity with a `backdrop-filter: blur(20px)`. This allows the vibrant marketplace colors to bleed through softly, anchoring the element in space.

---

## 3. Typography
The typography system is designed to handle the intricate beauty of Dari and Pashto scripts while maintaining modern legibility.

*   **Display & Headline (Plus Jakarta Sans):** Used for large price points and category headers. These should feel authoritative and bold. 
*   **Body & Labels (Inter):** Chosen for its exceptional legibility on mobile. In RTL contexts, ensure the line-height is increased by 15-20% compared to Latin standards to accommodate the taller ascenders and descenders of Persian/Pashto characters.
*   **Editorial Scaling:** Use high contrast between `display-lg` and `body-md`. This creates an "Editorial" hierarchy where the user’s eye is immediately drawn to the value proposition or product name, with secondary details receding into the background.

---

## 4. Elevation & Depth
In this design system, depth is a functional tool, not a decoration. We use **Tonal Layering** instead of structural lines.

*   **The Layering Principle:** Place a `surface_container_lowest` card on a `surface_container_low` section to create a soft, natural lift. This mimics how objects interact with light in the physical world.
*   **Ambient Shadows:** For floating elements (like a "Buy Now" FAB), use an extra-diffused shadow. 
    *   **Spec:** `box-shadow: 0px 12px 32px rgba(26, 28, 28, 0.06);` 
    *   The shadow color must be a tint of the `on_surface` color, never pure black.
*   **The "Ghost Border" Fallback:** If a container sits on a background of the same color and requires definition for accessibility, use a **Ghost Border**: the `outline-variant` token at 15% opacity. It should be felt, not seen.

---

## 5. Components

### Buttons
*   **Primary:** Large, `xl` (3rem) rounded corners. Use the signature gradient (Primary to Primary-Container). Text must be `on_primary`.
*   **Secondary:** `surface_container_highest` background with `on_surface` text. No border.
*   **Sizing:** All mobile buttons must have a minimum height of `12` (3rem) to ensure "Large Clickable" goals are met for mobile users.

### Cards & Marketplace Lists
*   **Strict Rule:** No dividers. Separate items using `8` (2rem) of vertical white space or by placing items in separate `surface_container_low` tiles.
*   **Image Handling:** Product images must use `lg` (2rem) corner radius. A very subtle `inset` ghost border can be used if the product image has a white background.

### Input Fields
*   **Style:** Use `surface_container_low` as the field background. 
*   **Focus State:** Transition the background to `surface_container_lowest` and apply a `primary` Ghost Border (20% opacity). 
*   **RTL Alignment:** Icons (Search, Location) must be mirrored for Persian/Pashto layouts, sitting on the opposite side of the text input.

### Chips (Category Filters)
*   **Style:** Pill-shaped (`full` roundedness). 
*   **Unselected:** `surface_container_high` with `on_surface_variant` text.
*   **Selected:** `primary` background with `on_primary` text.

---

## 6. Do's and Don'ts

### Do:
*   **Respect RTL Flow:** Ensure the visual weight of the screen starts from the right. This includes progress bars, chevron directions, and star ratings.
*   **Embrace White Space:** Use the `16` (4rem) spacing token for section padding to create a premium, unhurried shopping experience.
*   **Use Soft Corners:** Stick to `lg` (2rem) for cards and `xl` (3rem) for buttons to maintain the "Soft Minimalism" feel.

### Don't:
*   **Don't use 1px Dividers:** They clutter the UI and make it look like a generic template. Use tonal shifts.
*   **Don't use High-Contrast Shadows:** Avoid "drop shadows" that look like 2010-era design. If a shadow is visible as a "dark line," it is too heavy.
*   **Don't crowd the Text:** Afghan scripts require room. Never use a line-height less than 1.6 for body text in Dari or Pashto.
*   **Don't use Pure Black:** Use `secondary` (#17252A) or `on_surface` (#1a1c1c) for text to maintain a softer, more sophisticated contrast.