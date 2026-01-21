// src/routes/+page.ts
export const load = async ({ fetch }) => {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/courses');
        
        if (!response.ok) {
            console.error("API Error:", response.statusText);
            return { courses: [] }; 
        }

        const courses = await response.json();
        return { courses }; 

    } catch (error) {
        console.error("Fetch Error:", error);
        return { courses: [] };
    }
};