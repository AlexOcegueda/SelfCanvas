
export const load = async ({ fetch, params }) => {
    // Replace '1' with params.id if you are using dynamic routing
    const response = await fetch('http://127.0.0.1:5000/api/course/1'); 
    const course = await response.json();

    return {
        course
    };
};