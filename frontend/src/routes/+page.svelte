<script lang="ts">
    import { invalidateAll } from '$app/navigation';
    export let data;

    // --- CREATE COURSE STATE ---
    let showModal = false;
    let newCourseTitle = "";
    let isSubmitting = false;

    // --- CREATE FUNCTION ---
    async function handleCreateCourse() {
        if (!newCourseTitle.trim()) return;
        
        isSubmitting = true;
        
        const res = await fetch('https://canvasocegueda.pythonanywhere.com/api/courses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: newCourseTitle })
        });

        const result = await res.json();
        isSubmitting = false;

        if (res.ok) {
            showModal = false;
            newCourseTitle = "";
            await invalidateAll(); 
        } else {
            alert("Error: " + result.error);
        }
    }

    // --- DELETE FUNCTION ---
    async function handleDelete(id: number) {
        if (!confirm("Are you sure you want to delete this course? This cannot be undone.")) return;

        const res = await fetch(`https://canvasocegueda.pythonanywhere.com/api/courses/${id}`, {
            method: 'DELETE'
        });

        if (res.ok) {
            await invalidateAll(); 
        } else {
            alert("Failed to delete course");
        }
    }
</script>

<div class="max-w-4xl mx-auto p-8 relative">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">My Dashboard</h1>
        <button 
            on:click={() => showModal = true}
            class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 font-medium shadow-sm"
        >
            + Add New Course
        </button>
    </div>

    {#if data.courses.length === 0}
        <div class="text-center p-12 border-2 border-dashed border-gray-300 rounded-lg text-gray-500">
            <p class="text-lg">No courses found.</p>
            <button 
                on:click={() => showModal = true}
                class="text-blue-600 hover:underline mt-2"
            >
                Create your first course
            </button>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each data.courses as course}
                <div class="relative group border rounded-xl bg-white shadow-sm hover:shadow-md transition duration-200">
                    
                    <button 
                        on:click|preventDefault|stopPropagation={() => handleDelete(course.id)}
                        class="absolute top-3 right-3 z-20 p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors cursor-pointer"
                        title="Delete Course"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>

                    <a href="/course/{course.id}" class="block p-6 text-inherit no-underline">
                        <div class="h-24 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg mb-4 flex items-center justify-center text-white text-3xl font-bold shadow-inner">
                            {course.title.slice(0, 2).toUpperCase()}
                        </div>
                        
                        <h2 class="text-xl font-bold text-gray-900 truncate pr-8">{course.title}</h2>
                        <p class="text-gray-500 text-sm mt-1">View Assignments &rarr;</p>
                    </a>
                </div>
            {/each}
        </div>
    {/if}

    {#if showModal}
        <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
            <div class="bg-white p-6 rounded-lg shadow-xl w-96 transform transition-all scale-100">
                <h2 class="text-xl font-bold mb-4 text-gray-800">Add New Course</h2>
                
                <input 
                    type="text" 
                    bind:value={newCourseTitle}
                    placeholder="e.g. Intro to Computer Science"
                    class="w-full border p-2 rounded mb-6 focus:ring-2 focus:ring-blue-500 outline-none"
                    autofocus
                />
                
                <div class="flex justify-end gap-2">
                    <button 
                        on:click={() => showModal = false}
                        class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded"
                    >
                        Cancel
                    </button>
                    <button 
                        on:click={handleCreateCourse}
                        disabled={isSubmitting}
                        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                        {isSubmitting ? 'Creating...' : 'Create Course'}
                    </button>
                </div>
            </div>
        </div>
    {/if}
</div>