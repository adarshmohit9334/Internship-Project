CREATE TABLE profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id),
  personnel_no text UNIQUE NOT NULL,
  email text UNIQUE NOT NULL,
  name text,
  department text,
  designation text,
  mobile_no text,
  role text DEFAULT 'requester',
  manager_id uuid REFERENCES profiles(id)
);

-- BG Requests table
CREATE TABLE bg_requests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  requester_id uuid REFERENCES profiles(id),
  department text,
  location text,
  date_of_request date DEFAULT now(),
  work_order_no text,
  type_of_work text,
  job_value numeric,
  alternate_owner_id uuid REFERENCES profiles(id),
  party_name text,
  nature_of_bg text,
  bg_amount numeric,
  bg_expiry_date date,
  bg_claim_period text,
  remarks text,
  approval_level text,
  status text DEFAULT 'Draft',
  created_at timestamptz DEFAULT now(),
  decision_at timestamptz,
  decided_by uuid REFERENCES profiles(id),
  approval_remarks text
);

-- Attachments table
CREATE TABLE attachments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  bg_request_id uuid REFERENCES bg_requests(id),
  attachment_type text,
  file_path text,
  uploaded_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE bg_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE attachments ENABLE ROW LEVEL SECURITY;

-- Policies for bg_requests
-- Requesters can SELECT their own rows
CREATE POLICY select_own_bg_requests ON bg_requests
  FOR SELECT USING (auth.uid() = requester_id);

-- Requesters can INSERT their own rows
CREATE POLICY insert_own_bg_requests ON bg_requests
  FOR INSERT WITH CHECK (auth.uid() = requester_id);

-- Requesters can UPDATE their own rows
CREATE POLICY update_own_bg_requests ON bg_requests
  FOR UPDATE USING (auth.uid() = requester_id);

-- Admins can SELECT all rows
CREATE POLICY select_all_bg_requests_admin ON bg_requests
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin')
  );

-- Admins can UPDATE all rows
CREATE POLICY update_all_bg_requests_admin ON bg_requests
  FOR UPDATE USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin')
  );

-- Policies for attachments
-- Requesters can SELECT attachments for their own requests
CREATE POLICY select_own_attachments ON attachments
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM bg_requests WHERE id = attachments.bg_request_id AND requester_id = auth.uid())
  );

-- Requesters can INSERT attachments for their own requests
CREATE POLICY insert_own_attachments ON attachments
  FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM bg_requests WHERE id = attachments.bg_request_id AND requester_id = auth.uid())
  );

-- Admins can SELECT all attachments
CREATE POLICY select_all_attachments_admin ON attachments
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin')
  );
