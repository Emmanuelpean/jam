import React, {useEffect, useState} from 'react';
import {Dropdown} from 'react-bootstrap';

const BerryJamThemeToggle = () => {
    const [currentTheme, setCurrentTheme] = useState('mixed-berry');

    const themes = [
        {
            key: 'strawberry',
            name: 'Strawberry Jam',
            colors: {
                start: '#ff9a9e',
                mid: '#ff6b6b',
                end: '#c44569'
            },
            description: 'Sweet and vibrant'
        },
        {
            key: 'blueberry',
            name: 'Blueberry Jam',
            colors: {
                start: '#a8edea',
                mid: '#686de0',
                end: '#4834d4'
            },
            description: 'Deep and rich'
        },
        {
            key: 'raspberry',
            name: 'Raspberry Jam',
            colors: {
                start: '#ffecd2',
                mid: '#fd79a8',
                end: '#e84393'
            },
            description: 'Tart and bold'
        },
        {
            key: 'mixed-berry',
            name: 'Mixed Berry Jam',
            colors: {
                start: '#a29bfe',
                mid: '#6c5ce7',
                end: '#fd79a8'
            },
            description: 'Complex and layered'
        },
        {
            key: 'forest-berry',
            name: 'Forest Berry',
            colors: {
                start: '#d4e4d4',
                mid: '#a8b3a8',
                end: '#1a2e1a'
            },
            description: 'Natural and earthy'
        },
        {
            key: 'elderberry',
            name: 'Elderberry',
            colors: {
                start: '#e8d8f8',
                mid: '#b8a8c8',
                end: '#22183c'
            },
            description: 'Mysterious and refined'
        },
        {
            key: 'blackberry',
            name: 'Wild Blackberry',
            colors: {
                start: '#d8c8e8',
                mid: '#8a7a9a',
                end: '#0a0015'
            },
            description: 'Deep and sophisticated'
        }
    ];

    // Apply theme on component mount and when theme changes
    useEffect(() => {
        document.documentElement.setAttribute('data-theme', currentTheme);

        // Store theme preference in localStorage
        localStorage.setItem('berryJamTheme', currentTheme);
    }, [currentTheme]);

    // Load saved theme on component mount
    useEffect(() => {
        const savedTheme = localStorage.getItem('berryJamTheme');
        if (savedTheme && themes.find(theme => theme.key === savedTheme)) {
            setCurrentTheme(savedTheme);
        }
    }, []);

    const handleThemeChange = (themeKey) => {
        setCurrentTheme(themeKey);
    };

    const getCurrentTheme = () => {
        return themes.find(theme => theme.key === currentTheme);
    };

    const renderColorPreview = (colors) => (
        <div className="d-flex align-items-center me-2">
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
        </div>
    );

    return (
        <Dropdown>
            <Dropdown.Toggle
                className="btn-jam-primary d-flex align-items-center"
                style={{
                    background: `linear-gradient(135deg, ${getCurrentTheme().colors.start} 0%, ${getCurrentTheme().colors.mid} 50%, ${getCurrentTheme().colors.end} 100%)`,
                    border: 'none'
                }}
            >
                {renderColorPreview(getCurrentTheme().colors)}
                <span>{getCurrentTheme().name}</span>
            </Dropdown.Toggle>

            <Dropdown.Menu>
                <Dropdown.Header>
                    <small className="text-muted">Choose Berry Jam Theme</small>
                </Dropdown.Header>
                <Dropdown.Divider/>

                {themes.map((theme) => (
                    <Dropdown.Item
                        key={theme.key}
                        onClick={() => handleThemeChange(theme.key)}
                        active={currentTheme === theme.key}
                        className="d-flex align-items-center py-2"
                    >
                        {renderColorPreview(theme.colors)}
                        <div>
                            <div className="fw-medium">{theme.name}</div>
                            <small className="text-muted">{theme.description}</small>
                        </div>
                    </Dropdown.Item>
                ))}
            </Dropdown.Menu>
        </Dropdown>
    );
}

export default BerryJamThemeToggle;