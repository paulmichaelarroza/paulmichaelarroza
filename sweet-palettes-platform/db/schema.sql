CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin', 'staff', 'customer')),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE customers (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  full_name TEXT NOT NULL,
  phone TEXT,
  email TEXT,
  preferences JSONB DEFAULT '{}',
  segment TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE products (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT,
  price NUMERIC(10,2) NOT NULL,
  flavors JSONB,
  sizes JSONB,
  image_url TEXT,
  active BOOLEAN DEFAULT TRUE
);

CREATE TABLE orders (
  id UUID PRIMARY KEY,
  customer_id UUID REFERENCES customers(id),
  status TEXT NOT NULL CHECK (status IN ('Pending','Paid','Preparing','Out for delivery','Completed')),
  delivery_option TEXT NOT NULL CHECK (delivery_option IN ('Pickup','Delivery')),
  delivery_address TEXT,
  notes TEXT,
  subtotal NUMERIC(10,2) NOT NULL,
  delivery_fee NUMERIC(10,2) DEFAULT 0,
  total NUMERIC(10,2) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
  id UUID PRIMARY KEY,
  order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
  product_id UUID REFERENCES products(id),
  quantity INT NOT NULL,
  unit_price NUMERIC(10,2) NOT NULL,
  custom_notes TEXT
);

CREATE TABLE bookings (
  id UUID PRIMARY KEY,
  customer_id UUID REFERENCES customers(id),
  event_type TEXT NOT NULL,
  event_date DATE NOT NULL,
  event_location TEXT NOT NULL,
  guest_count INT NOT NULL,
  preferred_desserts JSONB,
  theme TEXT,
  budget_range TEXT,
  attachment_urls JSONB,
  status TEXT DEFAULT 'Pending',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE quotations (
  id UUID PRIMARY KEY,
  booking_id UUID REFERENCES bookings(id),
  package_tier TEXT,
  line_items JSONB NOT NULL,
  delivery_cost NUMERIC(10,2) DEFAULT 0,
  total_estimate NUMERIC(10,2) NOT NULL,
  pdf_url TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payments (
  id UUID PRIMARY KEY,
  order_id UUID REFERENCES orders(id),
  provider TEXT NOT NULL,
  provider_reference TEXT,
  amount NUMERIC(10,2) NOT NULL,
  status TEXT NOT NULL,
  paid_at TIMESTAMP
);

CREATE TABLE messages (
  id UUID PRIMARY KEY,
  customer_id UUID REFERENCES customers(id),
  channel TEXT NOT NULL CHECK (channel IN ('Messenger','WhatsApp','Website')),
  message_text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
