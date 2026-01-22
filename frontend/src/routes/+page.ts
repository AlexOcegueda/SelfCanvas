// src/routes/+page.ts
export const load = async ({ fetch }) => {
    try {
        // IMPORTANT: The { credentials: 'include' } part is likely missing!
        const res = await fetch('https://canvasocegueda.pythonanywhere.com/api/courses', {
            credentials: 'include' 
        });

        if (res.ok) {
            const courses = await res.json();
            return { courses };
        }
        
        return { courses: [] };
    } catch (e) {
        return { courses: [] };
    }
};