<script>
    // data is json format:
    // data = {"col1": [x1, x2, ...], "col2": [y1, y2, ...] ...}
    export let data;

</script>

<div class="overflow-x-auto">
    <table class="table table-xs table-pin-rows table-pin-cols">
        <thead>
            {#each data as col}
                <th>{col.col_name}</th>
            {/each}
        </thead>
        <tbody>
            {#each data as col}
                <tr>
                    {#each col.data as data}
                        <th>{data}</th>
                    {/each}
                </tr>
            {/each}
        </tbody>
        <!-- <tfoot>
            <tr>
                <th></th>
                <td>Name</td>
                <td>Job</td>
                <td>company</td>
                <td>location</td>
                <td>Last Login</td>
                <td>Favorite Color</td>
                <th></th>
            </tr>
        </tfoot> -->
    </table>
</div>
