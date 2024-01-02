<script>
    // TODO: Maybe switch to Chart.js?
    import * as d3 from 'd3';
    export let data;
    export let color_array;
    export let width = 640;
    export let height = 400;
    export let marginTop = 20;
    export let marginRight = 20;
    export let marginBottom = 30;
    export let marginLeft = 40;

    let gx;
    let gy;

    // Transforming the data to be compatible with d3.line
    $: formattedData = data.map(d => d.x.map((x, i) => ({x, y: d.y[i]})));

    $: x = d3.scaleLinear()
        .domain(d3.extent(formattedData.flat(), d => d.x))
        .range([marginLeft, width - marginRight]);

    $: y = d3.scaleLinear()
        .domain(d3.extent(formattedData.flat(), d => d.y))
        .range([height - marginBottom, marginTop]);

    $: line = d3.line()
        .x(d => x(d.x))
        .y(d => y(d.y));

    $: d3.select(gy).call(d3.axisLeft(y));
    $: d3.select(gx).call(d3.axisBottom(x));
</script>

{@debug color_array}
<svg {width} {height}>
    <g bind:this={gx} transform="translate(0,{height - marginBottom})" />
    <g bind:this={gy} transform="translate({marginLeft},0)" />
    {#each formattedData as d, i}
        <path fill="none" stroke="currentColor" stroke-width="3.5" d={line(d)} />
    {/each}
    {#each data as djson}
        <g fill={color_array[djson.uuid]} stroke={color_array[djson.uuid]} stroke-width="2.5">
            {#each djson.x as point, i}
                <circle cx={x(djson.x[i])} cy={y(djson.y[i])} r="2.5" />
            {/each}
        </g>
    {/each}
</svg>
