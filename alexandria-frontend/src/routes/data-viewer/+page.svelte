<script>
    import DataTable from "$lib/DataTable.svelte";
    import Plot_2d from "$lib/Plot_2d.svelte";
    import ColorPicker from 'svelte-awesome-color-picker';

    let start_hex = "#333333";
    let hex;
    $: point_color = hex;

    const test = [
        {"col_name": "col1", "type": "numeric", "data": [1,2,3,4]},
        {"col_name": "col1", "type": "numeric", "data": [1,2,3,4]},
        {"col_name": "col1", "type": "numeric", "data": [1,2,3,4]},
    ];

    let testData = [
        {
            'x': [1,2,3,4,5],
            'y': [1,3,5,7,12]
        },
        {
            'x': [6,7,8,9,10],
            'y': [1,5,4,2,1]
        }
    ];
</script>

<div class="flex-col m-2">
    <div class="text-xl">Data Viewer</div>
    <DataTable data={test} />
    <ul class="menu menu-horizontal px-1">
        <li>
            <details>
                <summary> Colors </summary>
                <ul class="p-2 bg-base-100 rounded-t-none">
                    <li>
                        <ColorPicker bind:hex label="color" />
                    </li>
                </ul>
            </details>
        </li>
    </ul>
    <h1>{point_color}</h1>
</div>
<Plot_2d data={testData} />
