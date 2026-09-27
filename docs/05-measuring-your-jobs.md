# 5. Measuring your GPU jobs

!!! clipboard-list "Lesson Objectives"

    - Recall what we are trying to achieve, and why measuring is the only way
      to get there
    - Know the four questions worth asking about a finished job
    - Know which tool answers which question

!!! clipboard-question "Questions"

    - I have submitted a job. What do I actually look at?
    - Which tool should I reach for, and when?

In this next section, we will look at how you test what GPU is appropriate for 
your job, as well as measure how namy CPUs and the amount of RAM you need
for your job. 

## Probing the GPU type, no of CPUs, and amount of RAM needed

Recall how we measure each of these three slurm tags:

1. **Which GPU do we use**: Follow this flow diagram:
    ![Choosing a GPU](./fig/choosing-a-gpu.png){: .center}
2. **How many core do we need**: Keep increasing the number of cores until the GPU efficiently does not change significantly
3. **How much RAM do I need**: Set high, record how much you need, then request that amount plus 20-30 % more. 

The next question is how to we measure the efficiency and vram of the GPU, the efficiency of the CPU, and the mount of RAM we need? In this section, we will look at the tools we can use to measure these.

