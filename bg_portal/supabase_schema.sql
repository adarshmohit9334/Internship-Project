CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  personnel_no TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  department TEXT,
  designation TEXT,
  mobile_no TEXT,
  role TEXT DEFAULT 'requester' CHECK (role IN ('requester', 'admin')),
  manager_id UUID REFERENCES profiles(id),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bg_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  requester_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  department TEXT NOT NULL,
  location TEXT NOT NULL,
  date_of_request DATE DEFAULT CURRENT_DATE,
  work_order_no TEXT NOT NULL,
  type_of_work TEXT NOT NULL,
  job_value NUMERIC(15,2) NOT NULL,
  alternate_owner_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  party_name TEXT NOT NULL,
  nature_of_bg TEXT NOT NULL CHECK (nature_of_bg IN ('Performance','Advance','Financial','Bid Bond')),
  bg_amount NUMERIC(15,2) NOT NULL,
  bg_expiry_date DATE NOT NULL,
  bg_claim_period TEXT NOT NULL,
  remarks TEXT,
  approval_level TEXT CHECK (approval_level IN ('MD','Board')),
  status TEXT DEFAULT 'Draft' CHECK (status IN ('Draft','Pending','Under Review','Approved','Rejected')),
  admin_remarks TEXT,
  decided_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
  decision_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS attachments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bg_request_id UUID REFERENCES bg_requests(id) ON DELETE CASCADE,
  attachment_type TEXT NOT NULL,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS activity_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bg_request_id UUID REFERENCES bg_requests(id) ON DELETE CASCADE,
  action_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
  action TEXT NOT NULL,
  old_status TEXT,
  new_status TEXT,
  note TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION set_approval_level()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.bg_amount <= 1500000 THEN
    NEW.approval_level := 'MD';
  ELSE
    NEW.approval_level := 'Board';
  END IF;
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER bg_requests_approval_level
BEFORE INSERT OR UPDATE ON bg_requests
FOR EACH ROW EXECUTE FUNCTION set_approval_level();

ALTER TABLE bg_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "requester_own_requests" ON bg_requests
  FOR ALL USING (requester_id = auth.uid());

CREATE POLICY IF NOT EXISTS "admin_all_requests" ON bg_requests
  FOR ALL USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin')
  );

CREATE POLICY IF NOT EXISTS "own_profile" ON profiles
  FOR ALL USING (id = auth.uid());

CREATE POLICY IF NOT EXISTS "admin_all_profiles" ON profiles
  FOR ALL USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin')
  );
