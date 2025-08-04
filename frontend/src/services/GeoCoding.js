// Cache to avoid repeated API calls for the same location
const geocodeCache = new Map();

export const geocodeLocation = async (location) => {
    // Skip remote locations
    if (location.remote) {
        return null;
    }

    // Build cache key from location data
    const cacheKey = [location.postcode, location.city, location.country]
        .filter(Boolean)
        .map(s => s.trim().toLowerCase())
        .join('|');

    if (!cacheKey) {
        return null;
    }

    // Check cache first
    if (geocodeCache.has(cacheKey)) {
        return geocodeCache.get(cacheKey);
    }

    try {
        // Build query string
        const queryParts = [];
        if (location.postcode?.trim()) queryParts.push(location.postcode.trim());
        if (location.city?.trim()) queryParts.push(location.city.trim());
        if (location.country?.trim()) queryParts.push(location.country.trim());

        if (queryParts.length === 0) {
            return null;
        }

        const query = queryParts.join(', ');

        // Use Nominatim geocoding service
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1&addressdetails=1`, {
            headers: {
                'User-Agent': 'LocationMapper/1.0'
            }
        });

        if (!response.ok) {
            throw new Error('Geocoding service unavailable');
        }

        const data = await response.json();

        if (data.length === 0) {
            // Cache null results to avoid repeated failed requests
            geocodeCache.set(cacheKey, null);
            return null;
        }

        const result = {
            latitude: parseFloat(data[0].lat), longitude: parseFloat(data[0].lon), displayName: data[0].display_name
        };

        // Cache the result
        geocodeCache.set(cacheKey, result);
        return result;

    } catch (error) {
        console.warn(`Failed to geocode location: ${cacheKey}`, error);
        // Cache null to avoid repeated failures
        geocodeCache.set(cacheKey, null);
        return null;
    }
};

// Batch geocode multiple locations with rate limiting
export const geocodeLocationsBatch = async (locations, onProgress = null) => {
    const results = [];
    const batchSize = 5; // Process 5 at a time to be respectful to the API
    const delay = 200; // 200ms delay between requests

    for (let i = 0; i < locations.length; i += batchSize) {
        const batch = locations.slice(i, i + batchSize);

        const batchPromises = batch.map(async (location) => {
            const coords = await geocodeLocation(location);
            return {
                ...location, geocoded: coords
            };
        });

        const batchResults = await Promise.all(batchPromises);
        results.push(...batchResults);

        // Report progress
        if (onProgress) {
            onProgress(Math.min(i + batchSize, locations.length), locations.length);
        }

        // Add delay between batches (except for the last batch)
        if (i + batchSize < locations.length) {
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }

    return results;
};

// Clear cache if needed
export const clearGeocodeCache = () => {
    geocodeCache.clear();
};