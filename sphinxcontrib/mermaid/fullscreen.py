"""
Fullscreen modal viewer functionality for Mermaid diagrams.

This module provides JavaScript and CSS templates for adding fullscreen
viewing capability to Mermaid diagrams with automatic dark/light theme detection.
"""

# CSS for fullscreen modal (theme-agnostic with JS-detected dark mode)
FULLSCREEN_CSS = """
.mermaid-container {
    position: relative !important;
    display: inline-block;
    width: 100%;
}

.mermaid-fullscreen-btn {
    position: absolute !important;
    width: 28px;
    height: 28px;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 0, 0, 0.3);
    border-radius: 4px;
    cursor: pointer;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    font-size: 14px;
    line-height: 1;
    padding: 0;
    color: #333;
}

.mermaid-fullscreen-btn:hover {
    background: rgba(255, 255, 255, 1);
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
    transform: scale(1.1);
}

.mermaid-fullscreen-btn.dark-theme {
    background: rgba(50, 50, 50, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: #e0e0e0;
}

.mermaid-fullscreen-btn.dark-theme:hover {
    background: rgba(60, 60, 60, 1);
    box-shadow: 0 3px 10px rgba(255, 255, 255, 0.2);
}

.mermaid-fullscreen-modal {
    display: none;
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw;
    height: 100vh;
    background: rgba(255, 255, 255, 0.98);
    z-index: 9999;
    padding: 20px;
    overflow: auto;
}

.mermaid-fullscreen-modal.dark-theme {
    background: rgba(0, 0, 0, 0.98);
}

.mermaid-fullscreen-modal.active {
    display: flex;
    align-items: center;
    justify-content: center;
}

.mermaid-fullscreen-content {
    position: relative;
    width: 95vw;
    height: 90vh;
    max-width: 95vw;
    max-height: 90vh;
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    overflow: auto;
    display: flex;
    align-items: center;
    justify-content: center;
}

.mermaid-fullscreen-content.dark-theme {
    background: #1a1a1a;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
}

.mermaid-fullscreen-content .mermaid {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.mermaid-fullscreen-content .mermaid svg {
    width: 100%;
    height: auto;
    max-width: 100%;
    max-height: 85vh;
    cursor: grab;
}

.mermaid-fullscreen-close {
    position: fixed !important;
    top: 20px !important;
    right: 20px !important;
    width: 40px;
    height: 40px;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 0, 0, 0.2);
    border-radius: 50%;
    cursor: pointer;
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    transition: all 0.2s;
    font-size: 24px;
    line-height: 1;
    color: #333;
}

.mermaid-fullscreen-close:hover {
    background: white;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
    transform: scale(1.1);
}

.mermaid-fullscreen-close.dark-theme {
    background: rgba(50, 50, 50, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #e0e0e0;
}

.mermaid-fullscreen-close.dark-theme:hover {
    background: rgba(60, 60, 60, 1);
    box-shadow: 0 6px 16px rgba(255, 255, 255, 0.2);
}

.mermaid-fullscreen-modal .mermaid-fullscreen-btn {
    display: none !important;
}
"""


# JavaScript for fullscreen (without D3 zoom)
MERMAID_RUN_FULLSCREEN = """
import mermaid from "{mermaid_js_url}";

const style = document.createElement('style');
style.textContent = `{fullscreen_css}`;
document.head.appendChild(style);

// Detect if page has dark background
const isDarkTheme = () => {{
    const bgColor = window.getComputedStyle(document.body).backgroundColor;
    const match = bgColor.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
    if (match) {{
        const r = parseInt(match[1]);
        const g = parseInt(match[2]);
        const b = parseInt(match[3]);
        const brightness = (r * 299 + g * 587 + b * 114) / 1000;
        return brightness < 128;
    }}
    return false;
}};

const initFullscreen = async () => {{
    await mermaid.run();

    const all_mermaids = document.querySelectorAll(".mermaid");
    const mermaids_processed = document.querySelectorAll(".mermaid[data-processed='true']");

    if(all_mermaids.length !== mermaids_processed.length) {{
        // Wait for mermaid to process all diagrams
        setTimeout(initFullscreen, 200);
        return;
    }}

    const darkTheme = isDarkTheme();

    const modal = document.createElement('div');
    modal.className = 'mermaid-fullscreen-modal' + (darkTheme ? ' dark-theme' : '');
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-label', 'Fullscreen diagram viewer');
    modal.innerHTML = `
        <button class="mermaid-fullscreen-close${{darkTheme ? ' dark-theme' : ''}}" aria-label="Close fullscreen">✕</button>
        <div class="mermaid-fullscreen-content${{darkTheme ? ' dark-theme' : ''}}"></div>
    `;
    document.body.appendChild(modal);

    const modalContent = modal.querySelector('.mermaid-fullscreen-content');
    const closeBtn = modal.querySelector('.mermaid-fullscreen-close');

    const closeModal = () => {{
        modal.classList.remove('active');
        modalContent.innerHTML = '';
        document.body.style.overflow = '';
    }};

    closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {{
        if (e.target === modal) closeModal();
    }});
    document.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape' && modal.classList.contains('active')) {{
            closeModal();
        }}
    }});

    const allButtons = [];

    document.querySelectorAll('.mermaid').forEach((mermaidDiv) => {{
        if (mermaidDiv.parentNode.classList.contains('mermaid-container') ||
            mermaidDiv.closest('.mermaid-fullscreen-modal')) {{
            return;
        }}

        const container = document.createElement('div');
        container.className = 'mermaid-container';
        mermaidDiv.parentNode.insertBefore(container, mermaidDiv);
        container.appendChild(mermaidDiv);

        const fullscreenBtn = document.createElement('button');
        fullscreenBtn.className = 'mermaid-fullscreen-btn' + (darkTheme ? ' dark-theme' : '');
        fullscreenBtn.setAttribute('aria-label', 'View diagram in fullscreen');
        fullscreenBtn.textContent = '{button_text}';

        // Calculate dynamic position based on diagram's margin and padding
        const diagramStyle = window.getComputedStyle(mermaidDiv);
        const marginTop = parseFloat(diagramStyle.marginTop) || 0;
        const marginRight = parseFloat(diagramStyle.marginRight) || 0;
        const paddingTop = parseFloat(diagramStyle.paddingTop) || 0;
        const paddingRight = parseFloat(diagramStyle.paddingRight) || 0;
        fullscreenBtn.style.top = `${{marginTop + paddingTop + 4}}px`;
        fullscreenBtn.style.right = `${{marginRight + paddingRight + 4}}px`;

        fullscreenBtn.addEventListener('click', () => {{
            const clone = mermaidDiv.cloneNode(true);
            modalContent.innerHTML = '';
            modalContent.appendChild(clone);

            const svg = clone.querySelector('svg');
            if (svg) {{
                svg.removeAttribute('width');
                svg.removeAttribute('height');
                svg.style.width = '100%';
                svg.style.height = 'auto';
                svg.style.maxWidth = '100%';
                svg.style.display = 'block';
            }}

            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }});

        container.appendChild(fullscreenBtn);
        allButtons.push(fullscreenBtn);
    }});

    // Update theme classes when theme changes
    const updateTheme = () => {{
        const dark = isDarkTheme();
        allButtons.forEach(btn => {{
            if (dark) {{
                btn.classList.add('dark-theme');
            }} else {{
                btn.classList.remove('dark-theme');
            }}
        }});
        if (dark) {{
            modal.classList.add('dark-theme');
            modalContent.classList.add('dark-theme');
            closeBtn.classList.add('dark-theme');
        }} else {{
            modal.classList.remove('dark-theme');
            modalContent.classList.remove('dark-theme');
            closeBtn.classList.remove('dark-theme');
        }}
    }};

    // Watch for theme changes
    const observer = new MutationObserver(updateTheme);
    observer.observe(document.documentElement, {{
        attributes: true,
        attributeFilter: ['class', 'style', 'data-theme']
    }});
    observer.observe(document.body, {{
        attributes: true,
        attributeFilter: ['class', 'style']
    }});
}};

window.addEventListener("load", initFullscreen);
"""


# JavaScript for fullscreen with D3 zoom
MERMAID_RUN_FULLSCREEN_ZOOM = """
import mermaid from "{mermaid_js_url}";

const style = document.createElement('style');
style.textContent = `{fullscreen_css}`;
document.head.appendChild(style);

// Detect if page has dark background
const isDarkTheme = () => {{
    const bgColor = window.getComputedStyle(document.body).backgroundColor;
    const match = bgColor.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
    if (match) {{
        const r = parseInt(match[1]);
        const g = parseInt(match[2]);
        const b = parseInt(match[3]);
        const brightness = (r * 299 + g * 587 + b * 114) / 1000;
        return brightness < 128;
    }}
    return false;
}};

const load = async () => {{
    await mermaid.run();
    const all_mermaids = document.querySelectorAll(".mermaid");
    const mermaids_to_add_zoom = {d3_node_count} === -1 ? all_mermaids.length : {d3_node_count};
    const mermaids_processed = document.querySelectorAll(".mermaid[data-processed='true']");
    if(mermaids_to_add_zoom > 0) {{
        var svgs = d3.selectAll("{d3_selector}");
        if(all_mermaids.length !== mermaids_processed.length) {{
            setTimeout(load, 200);
            return;
        }} else if(svgs.size() !== mermaids_to_add_zoom) {{
            setTimeout(load, 200);
            return;
        }} else {{
            svgs.each(function() {{
                var svg = d3.select(this);
                svg.html("<g class='wrapper'>" + svg.html() + "</g>");
                var inner = svg.select("g");
                var zoom = d3.zoom().on("zoom", function(event) {{
                    inner.attr("transform", event.transform);
                }});
                svg.call(zoom);
            }});
        }}
    }}

    const darkTheme = isDarkTheme();

    const modal = document.createElement('div');
    modal.className = 'mermaid-fullscreen-modal' + (darkTheme ? ' dark-theme' : '');
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-label', 'Fullscreen diagram viewer');
    modal.innerHTML = `
        <button class="mermaid-fullscreen-close${{darkTheme ? ' dark-theme' : ''}}" aria-label="Close fullscreen">✕</button>
        <div class="mermaid-fullscreen-content${{darkTheme ? ' dark-theme' : ''}}"></div>
    `;
    document.body.appendChild(modal);

    const modalContent = modal.querySelector('.mermaid-fullscreen-content');
    const closeBtn = modal.querySelector('.mermaid-fullscreen-close');

    const closeModal = () => {{
        modal.classList.remove('active');
        modalContent.innerHTML = '';
        document.body.style.overflow = '';
    }};

    closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {{
        if (e.target === modal) closeModal();
    }});
    document.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape' && modal.classList.contains('active')) {{
            closeModal();
        }}
    }});

    const allButtons = [];

    document.querySelectorAll('.mermaid').forEach((mermaidDiv) => {{
        if (mermaidDiv.parentNode.classList.contains('mermaid-container') ||
            mermaidDiv.closest('.mermaid-fullscreen-modal')) {{
            return;
        }}

        const container = document.createElement('div');
        container.className = 'mermaid-container';
        mermaidDiv.parentNode.insertBefore(container, mermaidDiv);
        container.appendChild(mermaidDiv);

        const fullscreenBtn = document.createElement('button');
        fullscreenBtn.className = 'mermaid-fullscreen-btn' + (darkTheme ? ' dark-theme' : '');
        fullscreenBtn.setAttribute('aria-label', 'View diagram in fullscreen');
        fullscreenBtn.textContent = '{button_text}';

        // Calculate dynamic position based on diagram's margin and padding
        const diagramStyle = window.getComputedStyle(mermaidDiv);
        const marginTop = parseFloat(diagramStyle.marginTop) || 0;
        const marginRight = parseFloat(diagramStyle.marginRight) || 0;
        const paddingTop = parseFloat(diagramStyle.paddingTop) || 0;
        const paddingRight = parseFloat(diagramStyle.paddingRight) || 0;
        fullscreenBtn.style.top = `${{marginTop + paddingTop + 4}}px`;
        fullscreenBtn.style.right = `${{marginRight + paddingRight + 4}}px`;

        fullscreenBtn.addEventListener('click', () => {{
            const clone = mermaidDiv.cloneNode(true);
            modalContent.innerHTML = '';
            modalContent.appendChild(clone);

            const svg = clone.querySelector('svg');
            if (svg) {{
                svg.removeAttribute('width');
                svg.removeAttribute('height');
                svg.style.width = '100%';
                svg.style.height = 'auto';
                svg.style.maxWidth = '100%';
                svg.style.display = 'block';

                setTimeout(() => {{
                    const g = svg.querySelector('g');
                    if (g) {{
                        var svgD3 = d3.select(svg);
                        svgD3.html("<g class='wrapper'>" + svgD3.html() + "</g>");
                        var inner = svgD3.select("g");
                        var zoom = d3.zoom().on("zoom", function(event) {{
                            inner.attr("transform", event.transform);
                        }});
                        svgD3.call(zoom);
                    }}
                }}, 100);
            }}

            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }});

        container.appendChild(fullscreenBtn);
        allButtons.push(fullscreenBtn);
    }});

    // Update theme classes when theme changes
    const updateTheme = () => {{
        const dark = isDarkTheme();
        allButtons.forEach(btn => {{
            if (dark) {{
                btn.classList.add('dark-theme');
            }} else {{
                btn.classList.remove('dark-theme');
            }}
        }});
        if (dark) {{
            modal.classList.add('dark-theme');
            modalContent.classList.add('dark-theme');
            closeBtn.classList.add('dark-theme');
        }} else {{
            modal.classList.remove('dark-theme');
            modalContent.classList.remove('dark-theme');
            closeBtn.classList.remove('dark-theme');
        }}
    }};

    // Watch for theme changes
    const observer = new MutationObserver(updateTheme);
    observer.observe(document.documentElement, {{
        attributes: true,
        attributeFilter: ['class', 'style', 'data-theme']
    }});
    observer.observe(document.body, {{
        attributes: true,
        attributeFilter: ['class', 'style']
    }});
}};

window.addEventListener("load", load);
"""
