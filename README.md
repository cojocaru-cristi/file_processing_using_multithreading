File_processing_using_multithreading

To get the results and to adequately compare them, a set of the same 50 files (images) were used for all the tests.

Timing results for downloading and processing files without involving any threading mechanism:

![image](https://user-images.githubusercontent.com/72966710/161107678-17e3737b-472c-4f8c-93a9-6672f996de23.png)

In the next step, the download method was addapted in order for it to use threads and the mechanisms that come with them (locks and semaphores).

The semaphore was used in order to specify the number of threads that can be opened at the same time. Once one of the original N threads is finished, another thread starts and so on.

Below there is a gradual increase in the maximum concurent threads allowed at the same time for downloading files:

N=1

![image](https://user-images.githubusercontent.com/72966710/161113101-cf0c1d5b-701f-4d01-81ea-fb36c405210c.png)

This result is comparable with the one we see when no threading is used.

N=5

![image](https://user-images.githubusercontent.com/72966710/161113777-d74a3390-e0a9-4b63-b557-c423308aaac3.png)

We can see here already a 3 time performance increase in terms of downloading the files.

N=10

![image](https://user-images.githubusercontent.com/72966710/161114319-f52bcb7f-642b-4957-991f-739c98cac36a.png)

Another few seconds lost in the process.


Now to further increase the performance on the file processing side a mechanism was used that involves queues and process pools. Threads are good to use, but there comes a point where opening many of them could result in some issues regarding resource sharing and syncronization. 

Queues and processes help with this aspect.

For image processing we can see a 3 time performance increase, with time spent on procesing images going under 1 second for the same batch of files.

![image](https://user-images.githubusercontent.com/72966710/161077243-e1b89cba-ad0e-48a8-8ff1-9699c4e63bbc.png)
