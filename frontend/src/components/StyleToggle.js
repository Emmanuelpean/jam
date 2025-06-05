import React, {useEffect, useState} from 'react';
import {Dropdown} from 'react-bootstrap';

const BerryJamThemeToggle = () => {
    const [currentTheme, setCurrentTheme] = useState('mixed-berry');
    const [currentColors, setCurrentColors] = useState({
        start: '#ffffff', mid: '#ffffff', end: '#ffffff'
    });

    const themes = [{
        key: 'strawberry', name: 'Strawberry Jam', description: 'Sweet and vibrant'
    }, {
        key: 'blueberry', name: 'Blueberry Jam', description: 'Deep and rich'
    }, {
        key: 'raspberry', name: 'Raspberry Jam', description: 'Tart and bold'
    }, {
        key: 'mixed-berry', name: 'Mixed Berry Jam', description: 'Complex and layered'
    }, {
        key: 'forest-berry', name: 'Forest Berry', description: 'Natural and earthy'
    }, {
        key: 'elderberry', name: 'Elderberry', description: 'Mysterious and refined'
    }, {
        key: 'blackberry', name: 'Wild Blackberry', description: 'Deep and sophisticated'
    }];

    // Function to get current CSS variable values
    const getCurrentCSSColors = () => {
        const computedStyle = getComputedStyle(document.documentElement);
        return {
            start: computedStyle.getPropertyValue('--primary-start').trim(),
            mid: computedStyle.getPropertyValue('--primary-mid').trim(),
            end: computedStyle.getPropertyValue('--primary-end').trim()
        };
    };

    // Apply theme and update colors
    useEffect(() => {
        document.documentElement.setAttribute('data-theme', currentTheme);

        // Store theme preference in localStorage
        localStorage.setItem('berryJamTheme', currentTheme);

        // Update current colors from CSS variables after theme change
        // Use setTimeout to ensure CSS has been updated
        setTimeout(() => {
            setCurrentColors(getCurrentCSSColors());
        }, 10);
    }, [currentTheme]);

    // Load saved theme on component mount
    useEffect(() => {
        const savedTheme = localStorage.getItem('berryJamTheme');
        if (savedTheme && themes.find(theme => theme.key === savedTheme)) {
            setCurrentTheme(savedTheme);
        }

        // Set initial colors
        setCurrentColors(getCurrentCSSColors());
    }, []);

    const handleThemeChange = (themeKey) => {
        setCurrentTheme(themeKey);
    };

    const getCurrentTheme = () => {
        return themes.find(theme => theme.key === currentTheme);
    };

    const renderColorPreview = (colors) => (<div className="d-flex align-items-center me-2">
        <div
            style={{
                width: '12px',
                height: '12px',
                backgroundColor: colors.start,
                borderRadius: '50%',
                marginRight: '2px',
                border: '1px solid rgba(255,255,255,0.3)'
            }}
        />
        <div
            style={{
                width: '12px',
                height: '12px',
                backgroundColor: colors.mid,
                borderRadius: '50%',
                marginRight: '2px',
                border: '1px solid rgba(255,255,255,0.3)'
            }}
        />
        <div
            style={{
                width: '12px',
                height: '12px',
                backgroundColor: colors.end,
                borderRadius: '50%',
                border: '1px solid rgba(255,255,255,0.3)'
            }}
        />
    </div>);

    // For dropdown items, we need to temporarily get colors for each theme
    const getThemeColors = (themeKey) => {
        // Temporarily apply theme to get colors
        const originalTheme = document.documentElement.getAttribute('data-theme');
        document.documentElement.setAttribute('data-theme', themeKey);
        const colors = getCurrentCSSColors();
        document.documentElement.setAttribute('data-theme', originalTheme);
        return colors;
    };

    // noinspection JSValidateTypes
    return (<Dropdown>
        <Dropdown.Toggle
            className="btn-jam-primary d-flex align-items-center"
            style={{
                background: `var(--primary-gradient)`, border: 'none'
            }}
        >
            {renderColorPreview(currentColors)}
            <span>{getCurrentTheme().name}</span>
        </Dropdown.Toggle>

        <Dropdown.Menu>
            <Dropdown.Header>
                <small className="text-muted">Choose Berry Jam Theme</small>
            </Dropdown.Header>
            <Dropdown.Divider/>

            {themes.map((theme) => {
                // Get preview colors for this theme
                const previewColors = getThemeColors(theme.key);

                return (<Dropdown.Item
                    key={theme.key}
                    onClick={() => handleThemeChange(theme.key)}
                    active={currentTheme === theme.key}
                    className="d-flex align-items-center py-2"
                >
                    {renderColorPreview(previewColors)}
                    <div>
                        <div className="fw-medium">{theme.name}</div>
                        <small className="text-muted">{theme.description}</small>
                    </div>
                </Dropdown.Item>);
            })}
        </Dropdown.Menu>
    </Dropdown>);
}

export default BerryJamThemeToggle;