import React, {useEffect, useState} from 'react';
import {Dropdown} from 'react-bootstrap';

const BerryJamThemeToggle = () => {
    const [currentTheme, setCurrentTheme] = useState('strawberry');

    const themes = [
        {
            key: 'strawberry',
            name: 'Strawberry Jam',
            colors: ['#ff6b6b', '#c44569'],
            description: 'Sweet and vibrant'
        },
        {
            key: 'blueberry',
            name: 'Blueberry Jam',
            colors: ['#4834d4', '#686de0'],
            description: 'Deep and rich'
        },
        {
            key: 'raspberry',
            name: 'Raspberry Jam',
            colors: ['#e84393', '#fd79a8'],
            description: 'Tart and bold'
        },
        {
            key: 'mixed-berry',
            name: 'Mixed Berry Jam',
            colors: ['#a29bfe', '#6c5ce7', '#fd79a8'],
            description: 'Complex and layered'
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
            {colors.map((color, index) => (
                <div
                    key={index}
                    style={{
                        width: '12px',
                        height: '12px',
                        backgroundColor: color,
                        borderRadius: '50%',
                        marginRight: index < colors.length - 1 ? '2px' : '0',
                        border: '1px solid rgba(255,255,255,0.3)'
                    }}
                />
            ))}
        </div>
    );

    return (
        <Dropdown>
            <Dropdown.Toggle
                className="btn-jam-primary d-flex align-items-center"
                style={{
                    background: `linear-gradient(135deg, ${getCurrentTheme().colors[0]} 0%, ${getCurrentTheme().colors[getCurrentTheme().colors.length - 1]} 100%)`,
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
};

export default BerryJamThemeToggle;