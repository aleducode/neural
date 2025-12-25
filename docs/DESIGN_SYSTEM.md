# Design System - Shadcn-Style Components

This document defines the design patterns and component structure for all admin screens. New screens should follow these guidelines to maintain visual consistency.

## Design Philosophy

- **Clean and minimal**: No gradients or heavy shadows on primary elements
- **Subtle borders**: Use `#e2e8f0` for borders instead of shadows
- **Proper spacing**: Consistent padding and margins using rem units
- **Professional typography**: Clear hierarchy with proper font weights
- **Muted colors**: Use slate color palette for text (`#0f172a`, `#64748b`, `#94a3b8`)

---

## Color Palette

### Text Colors
```css
--text-primary: #0f172a;      /* Headings, important text */
--text-secondary: #64748b;    /* Descriptions, labels */
--text-muted: #94a3b8;        /* Placeholders, hints */
```

### Border Colors
```css
--border-default: #e2e8f0;    /* Default borders */
--border-hover: #cbd5e1;      /* Hover state borders */
```

### Background Colors
```css
--bg-primary: #fff;           /* Cards, inputs */
--bg-secondary: #f8fafc;      /* Hover states, alternating rows */
--bg-tertiary: #f1f5f9;       /* Tags, filter tabs background */
```

### Status Colors
```css
/* Success/Online */
--success-bg: #dcfce7;
--success-text: #166534;
--success-dot: #22c55e;

/* Error/Offline */
--error-bg: #fef2f2;
--error-text: #991b1b;
--error-dot: #ef4444;

/* Primary actions */
--primary-bg: #0f172a;
--primary-hover: #1e293b;
```

---

## Components

### 1. Page Header

Simple header with title and description. No background colors or gradients.

```html
<div class="page-header">
  <div>
    <h4>Page Title</h4>
    <p>Brief description of the page purpose.</p>
  </div>
  <button class="btn-primary">
    <i class="ti ti-plus"></i>
    Action Button
  </button>
</div>
```

```css
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.page-header h4 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 0.25rem;
}

.page-header p {
  color: #64748b;
  font-size: 0.875rem;
  margin-bottom: 0;
}
```

### 2. Breadcrumb Navigation

Used for nested pages to show hierarchy.

```html
<nav class="breadcrumb-nav">
  <a href="/parent">Parent Page</a>
  <span class="separator">/</span>
  <span class="current">Current Page</span>
</nav>
```

```css
.breadcrumb-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 1rem;
}

.breadcrumb-nav a {
  color: #64748b;
  text-decoration: none;
  transition: color 0.15s ease;
}

.breadcrumb-nav a:hover {
  color: #0f172a;
}

.breadcrumb-nav .separator {
  color: #cbd5e1;
}

.breadcrumb-nav .current {
  color: #0f172a;
  font-weight: 500;
}
```

### 3. Stats Cards

Minimal cards for displaying key metrics.

```html
<div class="stats-card">
  <div class="stats-label">METRIC NAME</div>
  <div class="stats-value">42</div>
  <div class="stats-description">Additional context</div>
</div>
```

```css
.stats-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.25rem;
  transition: all 0.15s ease;
}

.stats-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}

.stats-card .stats-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.stats-card .stats-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1;
}

.stats-card .stats-description {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.5rem;
}
```

### 4. Main Card Container

Container for tables and list content.

```html
<div class="main-card">
  <div class="card-header-section">
    <!-- Header content -->
  </div>
  <!-- Table or list content -->
</div>
```

```css
.main-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  overflow: hidden;
}

.card-header-section {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.card-description {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0.125rem 0 0 0;
}
```

### 5. Search Input

Search input with icon.

```html
<div class="search-input-wrapper">
  <i class="ti ti-search search-icon"></i>
  <input type="text" class="search-input" placeholder="Search...">
</div>
```

```css
.search-input-wrapper {
  position: relative;
  width: 100%;
  max-width: 320px;
}

.search-input-wrapper .search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 2.25rem;
  padding: 0 0.75rem 0 2.25rem;
  font-size: 0.875rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  background: #fff;
  color: #0f172a;
  transition: all 0.15s ease;
}

.search-input::placeholder {
  color: #94a3b8;
}

.search-input:focus {
  outline: none;
  border-color: #0f172a;
  box-shadow: 0 0 0 1px #0f172a;
}
```

### 6. Filter Tabs

Pill-style filter tabs with counts.

```html
<div class="filter-tabs">
  <button class="filter-tab active" data-filter="all">
    All
    <span class="count">10</span>
  </button>
  <button class="filter-tab" data-filter="active">
    Active
    <span class="count">5</span>
  </button>
</div>
```

```css
.filter-tabs {
  display: flex;
  gap: 0.25rem;
  padding: 0.25rem;
  background: #f1f5f9;
  border-radius: 0.5rem;
}

.filter-tab {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #64748b;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.filter-tab:hover {
  color: #0f172a;
}

.filter-tab.active {
  background: #fff;
  color: #0f172a;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}

.filter-tab .count {
  font-size: 0.6875rem;
  padding: 0.125rem 0.375rem;
  background: #e2e8f0;
  border-radius: 9999px;
  color: #64748b;
}

.filter-tab.active .count {
  background: #0f172a;
  color: #fff;
}
```

### 7. Data Table

Clean table for displaying lists of data.

```html
<table class="data-table">
  <thead>
    <tr>
      <th>Column 1</th>
      <th>Column 2</th>
      <th style="text-align: right;">Actions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Data 1</td>
      <td>Data 2</td>
      <td><!-- Actions --></td>
    </tr>
  </tbody>
</table>
```

```css
.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.data-table th:first-child {
  padding-left: 1.5rem;
}

.data-table th:last-child {
  padding-right: 1.5rem;
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: middle;
}

.data-table td:first-child {
  padding-left: 1.5rem;
}

.data-table td:last-child {
  padding-right: 1.5rem;
}

.data-table tbody tr {
  transition: background 0.15s ease;
}

.data-table tbody tr:hover {
  background: #f8fafc;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}
```

### 8. Status Badge

Badge with colored dot indicator.

```html
<span class="status-badge online">
  <span class="status-dot"></span>
  Online
</span>

<span class="status-badge offline">
  <span class="status-dot"></span>
  Offline
</span>
```

```css
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 9999px;
}

.status-badge .status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
}

.status-badge.online {
  background: #dcfce7;
  color: #166534;
}

.status-badge.online .status-dot {
  background: #22c55e;
}

.status-badge.offline {
  background: #fef2f2;
  color: #991b1b;
}

.status-badge.offline .status-dot {
  background: #ef4444;
}
```

### 9. Tags

Small tags for displaying categories or assignments.

```html
<span class="tag">
  <i class="ti ti-brand-whatsapp"></i>
  Tag Name
</span>

<span class="tag tag-success">
  <i class="ti ti-world"></i>
  All Items
</span>
```

```css
.tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.1875rem 0.5rem;
  font-size: 0.6875rem;
  font-weight: 500;
  background: #f1f5f9;
  color: #475569;
  border-radius: 0.25rem;
  border: 1px solid #e2e8f0;
}

.tag i {
  font-size: 0.75rem;
}

.tag-success {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
  border: none;
}

.tag-success i {
  color: white;
}
```

### 10. Buttons

#### Primary Button
```html
<button class="btn-primary">
  <i class="ti ti-plus"></i>
  Primary Action
</button>
```

```css
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #fff;
  background: #0f172a;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s ease;
  text-decoration: none;
}

.btn-primary:hover {
  background: #1e293b;
  color: #fff;
}
```

#### Outline Button
```html
<button class="btn-outline">
  <i class="ti ti-settings"></i>
  Secondary Action
</button>
```

```css
.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #0f172a;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s ease;
  text-decoration: none;
}

.btn-outline:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #0f172a;
}
```

#### Icon Button (Toggle/Action)
```html
<button class="toggle-btn online">
  <i class="ti ti-power"></i>
</button>
```

```css
.toggle-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  border: 1px solid #e2e8f0;
  background: #fff;
  cursor: pointer;
  transition: all 0.15s ease;
}

.toggle-btn.online {
  color: #22c55e;
}

.toggle-btn.online:hover {
  background: #dcfce7;
  border-color: #bbf7d0;
}

.toggle-btn.offline {
  color: #ef4444;
}

.toggle-btn.offline:hover {
  background: #fef2f2;
  border-color: #fecaca;
}

.toggle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### 11. Empty State

Centered message when no data is available.

```html
<div class="empty-state">
  <div class="empty-state-icon">
    <i class="ti ti-users"></i>
  </div>
  <h5>No items found</h5>
  <p>Get started by adding your first item.</p>
  <button class="btn-primary">
    <i class="ti ti-plus"></i>
    Add Item
  </button>
</div>
```

```css
.empty-state {
  padding: 4rem 2rem;
  text-align: center;
}

.empty-state-icon {
  width: 4rem;
  height: 4rem;
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  border-radius: 9999px;
  color: #94a3b8;
  font-size: 1.5rem;
}

.empty-state-icon.success {
  background: #dcfce7;
  color: #16a34a;
}

.empty-state h5 {
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 0.5rem;
}

.empty-state p {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 1.5rem;
}
```

### 12. Toast Notifications

Bottom-right toast for feedback messages.

```html
<div class="toast-notification success">
  <i class="ti ti-check"></i>
  Action completed successfully
</div>
```

```css
.toast-notification {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  padding: 0.75rem 1rem;
  background: #0f172a;
  color: #fff;
  font-size: 0.875rem;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  animation: slideIn 0.3s ease;
}

.toast-notification.error {
  background: #dc2626;
}

.toast-notification.success {
  background: #16a34a;
}

@keyframes slideIn {
  from {
    transform: translateY(1rem);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```

### 13. List Items

For vertical lists with actions.

```html
<div class="list-item">
  <div class="list-item-icon assigned">
    <i class="ti ti-brand-whatsapp"></i>
  </div>
  <div class="list-item-content">
    <p class="list-item-title">Item Name</p>
    <p class="list-item-subtitle">Additional info</p>
  </div>
  <button class="list-item-action remove">
    <i class="ti ti-x"></i>
  </button>
</div>
```

```css
.list-item {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  transition: background 0.15s ease;
}

.list-item:last-child {
  border-bottom: none;
}

.list-item:hover {
  background: #f8fafc;
}

.list-item-icon {
  width: 40px;
  height: 40px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  flex-shrink: 0;
  margin-right: 0.75rem;
}

.list-item-icon.assigned {
  background: #dcfce7;
  color: #16a34a;
}

.list-item-icon.available {
  background: #f1f5f9;
  color: #64748b;
}

.list-item-content {
  flex: 1;
  min-width: 0;
}

.list-item-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #0f172a;
  margin-bottom: 0.125rem;
}

.list-item-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 0;
}

.list-item-action {
  width: 2rem;
  height: 2rem;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e2e8f0;
  background: #fff;
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.list-item-action.add {
  color: #16a34a;
}

.list-item-action.add:hover {
  background: #dcfce7;
  border-color: #bbf7d0;
}

.list-item-action.remove {
  color: #dc2626;
}

.list-item-action.remove:hover {
  background: #fef2f2;
  border-color: #fecaca;
}
```

### 14. Avatar

User avatar with initials and status-based colors.

```html
<div class="avatar online">JD</div>
<div class="avatar offline">JD</div>
```

```css
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  flex-shrink: 0;
}

.avatar.online {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
}

.avatar.offline {
  background: #f1f5f9;
  color: #64748b;
}

/* Large avatar variant */
.avatar-lg {
  width: 56px;
  height: 56px;
  font-size: 1.25rem;
}
```

---

## Spacing Guidelines

- **Page padding**: Use Bootstrap's `container-fluid`
- **Section margins**: `margin-bottom: 1.5rem` between major sections
- **Card padding**: `padding: 1.25rem 1.5rem`
- **Gap between elements**: `gap: 0.75rem` to `gap: 1rem`

## Typography Scale

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Page title | 1.5rem | 600 | #0f172a |
| Card title | 1rem | 600 | #0f172a |
| Body text | 0.875rem | 400 | #0f172a |
| Description | 0.875rem | 400 | #64748b |
| Label | 0.75rem | 500 | #64748b |
| Small text | 0.6875rem | 500 | #64748b |

## Border Radius Scale

| Use Case | Value |
|----------|-------|
| Cards | 0.75rem |
| Buttons | 0.375rem |
| Inputs | 0.375rem |
| Tabs container | 0.5rem |
| Badges/Pills | 9999px |
| Tags | 0.25rem |

## Transition

Always use: `transition: all 0.15s ease;`

---

## JavaScript Patterns

### Toast Notification Function
```javascript
function showToast(message, type = 'info') {
  const existing = document.querySelector('.toast-notification');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = `toast-notification ${type}`;
  toast.innerHTML = `
    <i class="ti ti-${type === 'success' ? 'check' : type === 'error' ? 'x' : 'info-circle'}"></i>
    ${message}
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}
```

### Filter Tab Switching
```javascript
document.querySelectorAll('.filter-tab').forEach(tab => {
  tab.addEventListener('click', function() {
    document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    this.classList.add('active');

    const filter = this.dataset.filter;
    const rows = document.querySelectorAll('.data-row');

    rows.forEach(row => {
      const status = row.dataset.status;
      row.style.display = (filter === 'all' || status === filter) ? '' : 'none';
    });
  });
});
```

### Search Filtering
```javascript
document.getElementById('search-input').addEventListener('input', function(e) {
  const query = e.target.value.toLowerCase().trim();
  const items = document.querySelectorAll('.searchable-item');

  items.forEach(item => {
    const searchText = item.dataset.searchText || '';
    item.style.display = searchText.includes(query) ? '' : 'none';
  });
});
```

---

## Example Screens Using This System

- `/conversations/agents/` - Agent list (data table with filters)
- `/conversations/agents/<id>/` - Agent detail (stats + list management)

When creating new admin screens, reference these existing implementations for consistent patterns.
