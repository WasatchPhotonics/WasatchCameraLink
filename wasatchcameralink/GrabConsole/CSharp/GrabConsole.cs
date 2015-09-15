using System;
using System.Collections.Generic;
using System.Text;
using System.IO;
using System.Runtime.InteropServices;

using DALSA.SaperaLT.SapClassBasic;
using DALSA.SaperaLT.Examples.NET.Utils;

namespace DALSA.SaperaLT.Examples.NET.CSharp.GrabConsole
{
    class GrabConsole
    {
        static int frame_count = 0;
        static void xfer_XferNotify(object sender, SapXferNotifyEventArgs args)
        {
            SapView View = args.Context as SapView;
            View.Show();
        }


        static void Main(string[] args)
        {

            SapAcquisition Acq = null;
            SapAcqDevice AcqDevice = null;
            SapBuffer Buffers = null;
            SapTransfer Xfer = null;
            SapView View = null;

            //Console.WriteLine("Sapera Console Grab Example (C# version)\n");

            MyAcquisitionParams acqParams = new MyAcquisitionParams();

            // Call GetOptions to determine which acquisition device to use and which config
            // file (CCF) should be loaded to configure it.
            if (!GetOptions(args, acqParams))
            {
                Console.WriteLine("\nPress any key to terminate\n");
                Console.ReadKey(true);
                return;
            }

            SapLocation loc = new SapLocation(acqParams.ServerName, acqParams.ResourceIndex);

            if (SapManager.GetResourceCount(acqParams.ServerName, SapManager.ResourceType.Acq) > 0)
            {
                Acq         = new SapAcquisition(loc, acqParams.ConfigFileName);
                Buffers     = new SapBuffer(1, Acq, SapBuffer.MemoryType.ScatterGather);
                Xfer = new SapAcqToBuf(Acq, Buffers);                

               // Create acquisition object
                if (!Acq.Create())
                {
                    Console.WriteLine("Error during SapAcquisition creation!\n");
                    DestroysObjects(Acq, AcqDevice, Buffers, Xfer, View);
                    return;
                }
            }

            if (SapManager.GetResourceCount(acqParams.ServerName, SapManager.ResourceType.AcqDevice) > 0)
            {
                AcqDevice   = new SapAcqDevice(loc, acqParams.ConfigFileName);
                Buffers = new SapBuffer(1, AcqDevice, SapBuffer.MemoryType.ScatterGather);
                Xfer = new SapAcqDeviceToBuf(AcqDevice, Buffers);
          
               // Create acquisition object
                if (!AcqDevice.Create())
                {
                    Console.WriteLine("Error during SapAcqDevice creation!\n");
                    DestroysObjects(Acq, AcqDevice, Buffers, Xfer, View);
                    return;
                }
            }

            View = new SapView(Buffers);
            // End of frame event
            Xfer.Pairs[0].EventType = SapXferPair.XferEventType.EndOfFrame;
            Xfer.XferNotify += new SapXferNotifyHandler(xfer_XferNotify);
            Xfer.XferNotifyContext = View;

            //Console.WriteLine("gggggwhat is new line");
            // Create buffer object
            if (!Buffers.Create())
            {
                Console.WriteLine("Error during SapBuffer creation!\n");
                DestroysObjects(Acq, AcqDevice, Buffers, Xfer, View);
                return;
            }

            // Create buffer object
            if (!Xfer.Create())
            {
                Console.WriteLine("Error during SapTransfer creation!\n");
                DestroysObjects(Acq, AcqDevice, Buffers, Xfer, View);
                return;
            }

            // Create buffer object
            if (!View.Create())
            {
                Console.WriteLine("Error during SapView creation!\n");
                DestroysObjects(Acq, AcqDevice, Buffers, Xfer, View);
                return;
            }

            // Grab as fast as possible, wait for a key to be pressed, if it's p, 
            // write the file, otherwise if it's q exit the program. Designed to be run by and monitored 
            // through a pipe

            Boolean stop_snap = false;
            int curr_code = 0;
            string new_cmd = "";
            while (stop_snap == false)
            {
                Console.WriteLine("Press a key to trigger snap");
                new_cmd = Console.ReadLine();
                Xfer.Snap();

                Console.WriteLine("Press a key to trigger save");
                new_cmd = Console.ReadLine();
                View.Buffer.Save("test.raw", "-format raw");

                var dsb = new StringBuilder("frame: " + frame_count);
                Console.WriteLine(dsb);
                frame_count = frame_count + 1;


                Console.WriteLine("File saved, Press a key to repeat, q to quit:");
                new_cmd = Console.ReadLine();
                if (new_cmd == "q") { stop_snap = true; }
                //if (curr_code == 113) { stop_snap = true; }

            }
            
            DestroysObjects(Acq, AcqDevice, Buffers, Xfer, View);
            loc.Dispose();
        }


        static bool GetOptions(string[] args, MyAcquisitionParams acqParams)
        {
           // Check if arguments were passed
           if (args.Length > 1)
               return ExampleUtils.GetOptionsFromCommandLine(args, acqParams);
           else
              return ExampleUtils.GetOptionsFromQuestions(acqParams);
        }
      

        static void DestroysObjects(SapAcquisition acq, SapAcqDevice camera, SapBuffer buf, SapTransfer xfer, SapView view)
        {

            if (xfer != null)
            {
                xfer.Destroy();
                xfer.Dispose();
            }

            if (camera != null)
            {
                camera.Destroy();
                camera.Dispose();
            }

            if (acq != null)
            {
                acq.Destroy();
                acq.Dispose();
            }

            if (buf != null)
            {
                buf.Destroy();
                buf.Dispose();
            }

            if (view != null)
            {
                view.Destroy();
                view.Dispose();
            }

            //Console.WriteLine("\nPress any key to terminate\n");
            //Console.ReadKey(true);
        }
    }
}
