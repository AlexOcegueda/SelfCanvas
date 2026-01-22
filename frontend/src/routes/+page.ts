// src/routes/+page.ts
export const load = async ({ fetch }) => {
    try {
        const response = await fetch('https://canvasocegueda.pythonanywhere.com/api/courses', {
            credentials: 'include' 
        });
        
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