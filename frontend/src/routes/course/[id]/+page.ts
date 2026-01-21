// src/routes/course/[id]/+page.ts
export const load = async ({ fetch, params }) => {
    
    const response = await fetch(`http://127.0.0.1:5000/api/course/${params.id}`);
    
    if (!response.ok) {
        throw new Error("Course not found in database");
    }

    const course = await response.json();
    
    return {
        course
    };
};