// src/routes/course/[id]/+page.ts
import { error } from '@sveltejs/kit';

export const load = async ({ fetch, params }) => {
    const res = await fetch(`https://canvasocegueda.pythonanywhere.com/api/course/${params.id}`, {
        credentials: 'include' 
    });

    if (res.ok) {
        const course = await res.json();
        return { course };
    }

    // If 404 or 401, return a safe empty object so the page doesn't crash
    return { 
        course: { title: 'Course Not Found', modules: [] } 
    };
};