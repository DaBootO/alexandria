<script>
    import { writable } from 'svelte/store';
    import DataTable from "$lib/DataTable.svelte";
    import Plot_2d from "$lib/Plot_2d.svelte";
    import ColorPicker from 'svelte-awesome-color-picker';

    const test = [
        {
            "col_name": "col1",
            "uuid": "abcdefg",
            "type": "numeric",
            "data": [1,2,3,4]
        },
        {
            "col_name": "col2",
            "uuid": "hijklmo",
            "type": "numeric",
            "data": [1,2,3,4]
        },
    ];

    let testData = [
        {
            'uuid': 'abcdefg',
            'x': [1,2,3,4,5],
            'y': [1,3,5,7,12]
        },
        {
            'uuid': 'hijklmo',
            'x': [6,7,8,9,10],
            'y': [1,5,4,2,1]
        }
    ];
    
    
    let color_array = writable({});
    // Handle color change
    function handle_color(uuid, hex) {
        color_array.update(values => ({ ...values, [uuid]: hex }));
    }

</script>

<div class="flex-col m-2">
    <div class="text-xl">Data Viewer</div>
    <DataTable data={test} />
    <ul class="menu menu-horizontal px-1 focus">
        <li>
            <details>
                <summary> Colors </summary>
                <ul class="p-2 bg-base-100 rounded-t-none">
                    {#each test as t}
                        <li>
                            <ColorPicker bind:hex={$color_array[t.uuid]} on:input={() => handle_color(t.uuid, $color_array[t.uuid])} label={t.uuid} />
                        </li>
                    {/each}
                </ul>
            </details>
        </li>
    </ul>
</div>
<Plot_2d bind:data={testData} bind:color_array={$color_array} />
