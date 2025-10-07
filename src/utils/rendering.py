import streamlit as st

# -------------------
# Auto-scroll to latest message (Improved)
# -------------------
def scroll_to_bottom():
    st.markdown("""
    <script>
    function scrollToBottom() {
        const target = window.parent.document;

        // Method 1: Target the main Streamlit container
        const mainContainer = target.querySelector('.main');
        if (mainContainer) {
            mainContainer.scrollTop = mainContainer.scrollHeight;
            return;
        }

        // Method 2: Target Streamlit's scrollable area
        const scrollContainers = target.querySelectorAll('[data-testid="stVerticalBlock"]');
        if (scrollContainers.length > 0) {
            const lastContainer = scrollContainers[scrollContainers.length - 1];
            lastContainer.scrollTop = lastContainer.scrollHeight;
            return;
        }

        // Method 3: Scroll the entire window as fallback
        window.parent.scrollTo(0, document.body.scrollHeight);
    }

    // Try multiple times with increasing delays to catch dynamic content
    [100, 500, 1000, 1500].forEach(delay => {
        setTimeout(scrollToBottom, delay);
    });

    // Also scroll when window resizes (handles mobile/tablet)
    window.addEventListener('resize', scrollToBottom);
    </script>
    """, unsafe_allow_html=True)
