<script lang="ts">
    export let data; // This receives the { courses } from the file above
</script>

<div class="max-w-4xl mx-auto p-8">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">My Dashboard</h1>
    </div>

    {#if data.courses.length === 0}
        <div class="text-center p-10 border-2 border-dashed rounded-lg text-gray-500">
            <p class="text-lg">No courses found.</p>
            <p class="text-sm mt-2">Make sure your Python backend is running!</p>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each data.courses as course}
                <a 
                    href="/course/{course.id}" 
                    class="block border rounded-lg p-6 bg-white shadow-sm hover:shadow-md transition text-inherit no-underline"
                >
                    <div class="h-24 bg-blue-600 rounded-md mb-4 flex items-center justify-center text-white text-3xl font-bold opacity-90">
                        {course.title.slice(0, 2).toUpperCase()}
                    </div>
                    
                    <h2 class="text-xl font-bold text-gray-900">{course.title}</h2>
                    <p class="text-gray-500 text-sm mt-1">View Syllabus & Assignments &rarr;</p>
                </a>
            {/each}
        </div>
    {/if}
</div>