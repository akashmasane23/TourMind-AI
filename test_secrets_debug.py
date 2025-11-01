import streamlit as st
import os

st.title("🔍 Secrets Debug Test")

# Check file exists
secrets_path = ".streamlit/secrets.toml"
st.success(f"✅ File exists at: {os.path.abspath(secrets_path)}")

# Show file content
st.markdown("### File Contents:")
with open(secrets_path, 'r') as f:
    content = f.read()
    st.code(content, language="toml")

st.markdown("---")

# Try to load with Streamlit
st.markdown("### Streamlit Secrets Loading:")
try:
    # Show all secrets
    st.write("**All secrets:**")
    st.json(dict(st.secrets))
    
    # Show api_keys section
    st.write("**API Keys section:**")
    api_keys = dict(st.secrets["api_keys"])
    
    # Mask keys for security (show only last 4 characters)
    for key, value in api_keys.items():
        if value and len(value) > 4:
            api_keys[key] = "***" + value[-4:]
        else:
            api_keys[key] = "NOT SET"
    
    st.json(api_keys)
    
    st.success("✅ Secrets loaded successfully!")
    
except KeyError as e:
    st.error(f"❌ KeyError: {e}")
    st.info("Make sure your secrets.toml has the correct structure")
    
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.info("Check your secrets.toml file format")
