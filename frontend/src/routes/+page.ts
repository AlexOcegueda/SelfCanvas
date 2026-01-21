// src/routes/+page.ts
export const load = async ({ fetch }) => {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/courses');
        
        if (!response.ok) {
            console.error("API Error:", response.statusText);
            return { courses: [] }; // Return empty list if API fails
        }

        const courses = await response.json();
        return { courses }; // Pass the list to the UI

    } catch (error) {
        console.error("Fetch Error:", error);
        return { courses: [] };
    }
};