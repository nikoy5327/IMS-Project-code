INSERT INTO roles (role_name, allowed_actions)
VALUES ('admin', '["ALL"]');

INSERT INTO users (username, password_hash, role_id)
VALUES ('username', '$2b$12$fL/3gWwtXajH.kNsMVCf5OqZ1XcYeB/XGuvsrMRZYqRATvv25LEay', 1);
