-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
  user_id uuid PRIMARY KEY,
  name text,
  age int,
  gender text,
  class_level int,
  stream text,
  location jsonb,
  language_preference text,
  budget_range text,
  reservation_category text,
  mobility text,
  created_at timestamptz DEFAULT now()
);

-- Create quizzes table
CREATE TABLE IF NOT EXISTS quizzes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES profiles(user_id),
  quiz_json jsonb,
  source text,
  created_at timestamptz DEFAULT now()
);

-- Create quiz_responses table for storing submitted answers
CREATE TABLE IF NOT EXISTS quiz_responses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES profiles(user_id),
  quiz_id uuid REFERENCES quizzes(id),
  answers jsonb,
  created_at timestamptz DEFAULT now()
);
